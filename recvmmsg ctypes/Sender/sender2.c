// UDP ramp load generator (sendmmsg, multi-thread). Test ONLY your own server.
// Packet: magic(1)=0xA5 | ver(1)=1 | device(4) | seq(4) | ts_ms(8) | value(f32) | zero pad to 64, big-endian
#define _GNU_SOURCE
#include <arpa/inet.h>
#include <endian.h>
#include <errno.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define RECSZ 64
#define VLEN 256
#define MAXSOCK 16
#define MAXTHR 64

static atomic_ullong g_sent;
static atomic_ullong g_rate;   // current total target pps, 0 = unlimited
static atomic_int g_step;
static atomic_int g_stop;

typedef struct {
    struct sockaddr_in dst;
    int id, nsock, nthreads;
} arg_t;

static double mono(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

static void *worker(void *p) {
    arg_t *a = p;
    int fds[MAXSOCK];
    for (int i = 0; i < a->nsock; i++) {
        fds[i] = socket(AF_INET, SOCK_DGRAM, 0);
        int sb = 16 << 20;
        setsockopt(fds[i], SOL_SOCKET, SO_SNDBUF, &sb, sizeof sb);
        if (connect(fds[i], (struct sockaddr *)&a->dst, sizeof a->dst) < 0) {
            perror("connect");
            return NULL;
        }
    }

    static __thread uint8_t bufs[VLEN][RECSZ];
    struct iovec iov[VLEN];
    struct mmsghdr msgs[VLEN];
    uint32_t seq[VLEN];
    memset(bufs, 0, sizeof bufs);
    memset(msgs, 0, sizeof msgs);
    float v = 1.5f;
    uint32_t vbits;
    memcpy(&vbits, &v, 4);
    vbits = htonl(vbits);
    for (int i = 0; i < VLEN; i++) {
        bufs[i][0] = 0xA5;
        bufs[i][1] = 1;
        uint32_t dev = htonl((uint32_t)(a->id * VLEN + i));
        memcpy(&bufs[i][2], &dev, 4);
        memcpy(&bufs[i][18], &vbits, 4);
        seq[i] = 0;
        iov[i].iov_base = bufs[i];
        iov[i].iov_len = RECSZ;
        msgs[i].msg_hdr.msg_iov = &iov[i];
        msgs[i].msg_hdr.msg_iovlen = 1;
    }

    int my_step = -1, k = 0;
    double t0 = 0;
    uint64_t local = 0;
    while (!atomic_load_explicit(&g_stop, memory_order_relaxed)) {
        int st = atomic_load_explicit(&g_step, memory_order_relaxed);
        if (st != my_step) {            // new ramp step: restart pacing window
            my_step = st;
            t0 = mono();
            local = 0;
        }
        struct timespec rt;
        clock_gettime(CLOCK_REALTIME, &rt);
        uint64_t ms = htobe64((uint64_t)rt.tv_sec * 1000 + rt.tv_nsec / 1000000);
        for (int i = 0; i < VLEN; i++) {
            uint32_t s = htonl(++seq[i]);
            memcpy(&bufs[i][6], &s, 4);
            memcpy(&bufs[i][10], &ms, 8);
        }

        int n = sendmmsg(fds[k++ % a->nsock], msgs, VLEN, 0);
        if (n > 0) {
            local += n;
            atomic_fetch_add_explicit(&g_sent, n, memory_order_relaxed);
        } else if (n < 0 && errno != EINTR && errno != EAGAIN &&
                   errno != ENOBUFS && errno != ECONNREFUSED) {
            perror("sendmmsg");
            break;
        }

        uint64_t rate = atomic_load_explicit(&g_rate, memory_order_relaxed) / a->nthreads;
        if (rate) {
            double ahead = (double)local / rate - (mono() - t0);
            if (ahead > 0.0002) {
                struct timespec ts = {(time_t)ahead, (long)((ahead - (time_t)ahead) * 1e9)};
                nanosleep(&ts, NULL);
            }
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr,
                "usage: %s HOST [PORT=9999] [THREADS=3] [SOCKS=4] [START=200000] [STEP=200000] [MAX=2000000] [STEP_SEC=5]\n"
                "  ramps the target rate START, START+STEP, ... up to MAX, STEP_SEC seconds each.\n"
                "  MAX=0 -> single unlimited step (maximum speed).\n",
                argv[0]);
        return 1;
    }
    const char *host = argv[1];
    int port = argc > 2 ? atoi(argv[2]) : 9999;
    int threads = argc > 3 ? atoi(argv[3]) : 3;
    int socks = argc > 4 ? atoi(argv[4]) : 4;
    unsigned long long start = argc > 5 ? strtoull(argv[5], NULL, 10) : 200000;
    unsigned long long step = argc > 6 ? strtoull(argv[6], NULL, 10) : 200000;
    unsigned long long max = argc > 7 ? strtoull(argv[7], NULL, 10) : 2000000;
    double step_sec = argc > 8 ? atof(argv[8]) : 5;
    if (threads > MAXTHR) threads = MAXTHR;
    if (threads < 1) threads = 1;
    if (socks > MAXSOCK) socks = MAXSOCK;
    if (socks < 1) socks = 1;

    struct sockaddr_in dst = {0};
    dst.sin_family = AF_INET;
    dst.sin_port = htons(port);
    if (inet_pton(AF_INET, host, &dst.sin_addr) != 1) {
        fprintf(stderr, "bad host\n");
        return 1;
    }

    pthread_t th[MAXTHR];
    arg_t args[MAXTHR];
    for (int i = 0; i < threads; i++) {
        args[i] = (arg_t){dst, i, socks, threads};
        pthread_create(&th[i], NULL, worker, &args[i]);
    }

    unsigned long long rate = max ? start : 0;
    unsigned long long best = 0;
    double t_all = mono();
    printf("%-12s %-12s %s\n", "target/s", "actual/s", "note");
    for (;;) {
        atomic_store(&g_rate, rate);
        atomic_fetch_add(&g_step, 1);
        sleep(1);                                   // let pacing settle
        unsigned long long c0 = atomic_load(&g_sent);
        double t0 = mono();
        usleep((useconds_t)((step_sec - 1 > 1 ? step_sec - 1 : 1) * 1e6));
        unsigned long long c1 = atomic_load(&g_sent);
        double actual = (c1 - c0) / (mono() - t0);
        if ((unsigned long long)actual > best) best = (unsigned long long)actual;
        const char *note = (rate && actual < rate * 0.95) ? "<- sender cannot reach target" : "";
        printf("%-12llu %-12.0f %s\n", rate, actual, note);
        fflush(stdout);
        if (!max || rate >= max) break;
        rate += step;
        if (rate > max) rate = max;
    }
    atomic_store(&g_stop, 1);
    for (int i = 0; i < threads; i++) pthread_join(th[i], NULL);
    unsigned long long total = atomic_load(&g_sent);
    printf("\nTotal sent = %llu in %.1fs, best sustained = %llu pkt/s\n", total, mono() - t_all, best);
    printf("Compare with the server's FINAL recv. The difference is lost packets.\n");
    return 0;
}
