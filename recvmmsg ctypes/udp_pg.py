#!/usr/bin/env python3
"""UDP ingest server -> PostgreSQL (single file).

recvmmsg batched receive + SO_REUSEPORT multi-process + numpy validation
+ binary COPY into PostgreSQL from a writer thread in every process.

Packet format (exactly RECSZ bytes, big-endian):
  magic(1)=0xA5 | version(1)=1 | device_id(4) | seq(4) | ts_ms(8) | value(float32, 4) | zero padding to 64

Run:
  python udp_pg.py --procs 4 --db-url "postgresql://localhost/mydb"
  python udp_pg.py --procs 4            # test mode: no database, data is discarded
"""
import argparse, asyncio, ctypes, ctypes.util, io, logging, os, queue, signal
import socket, struct, sys, threading, time
import multiprocessing as mp
from ctypes import c_void_p, c_size_t, c_uint32, c_int, c_uint, POINTER

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ingest")

RECSZ = 64                  # fixed packet size in bytes
MAGIC, VERSION = 0xA5, 1
MSG_WAITFORONE = 0x10000
EINTR, EAGAIN = 4, 11

# per-process counter slots (shared memory)
RECV, BADLEN, DROPPED, BADMAGIC, WRITTEN, FAILED = range(6)
NSLOT = 6

# packet layout inside one 64-byte record
IN = np.dtype({
    "names":   ["magic", "ver", "dev", "seq", "ts", "val"],
    "formats": ["u1", "u1", ">u4", ">u4", ">u8", ">f4"],
    "offsets": [0, 1, 2, 6, 10, 18],
    "itemsize": RECSZ,
})

# one PostgreSQL binary-COPY row: field count, then (length, data) per column
ROW = np.dtype([("n", ">i2"),
                ("l1", ">i4"), ("dev", ">i8"),
                ("l2", ">i4"), ("seq", ">i8"),
                ("l3", ">i4"), ("ts", ">i8"),
                ("l4", ">i4"), ("val", ">f4")])
HEADER = b"PGCOPY\n\xff\r\n\x00" + struct.pack(">ii", 0, 0)
TRAILER = struct.pack(">h", -1)

COLUMNS = ["device_id", "seq", "ts_ms", "value"]


def schema_sql(unlogged):
    return f"""
CREATE {'UNLOGGED ' if unlogged else ''}TABLE IF NOT EXISTS readings (
    device_id BIGINT,
    seq       BIGINT,
    ts_ms     BIGINT,
    value     REAL
)"""


async def init_schema(dsn, unlogged):
    import asyncpg
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute(schema_sql(unlogged))
    finally:
        await conn.close()


# ---------------------------------------------------------------- C structs
class iovec(ctypes.Structure):
    _fields_ = [("iov_base", c_void_p), ("iov_len", c_size_t)]

class msghdr(ctypes.Structure):
    _fields_ = [("msg_name", c_void_p), ("msg_namelen", c_uint32),
                ("msg_iov", POINTER(iovec)), ("msg_iovlen", c_size_t),
                ("msg_control", c_void_p), ("msg_controllen", c_size_t),
                ("msg_flags", c_int)]

class mmsghdr(ctypes.Structure):
    _fields_ = [("msg_hdr", msghdr), ("msg_len", c_uint)]


def load_libc():
    for name in (ctypes.util.find_library("c"), "libc.so", "libc.so.6"):
        if name:
            try:
                return ctypes.CDLL(name, use_errno=True)
            except OSError:
                pass
    raise OSError("libc not found")


# ------------------------------------------------------------------ writer
def to_copy_bytes(rec):
    r = np.empty(len(rec), dtype=ROW)
    r["n"] = 4
    r["l1"] = r["l2"] = r["l3"] = 8
    r["l4"] = 4
    r["dev"], r["seq"], r["ts"], r["val"] = rec["dev"], rec["seq"], rec["ts"], rec["val"]
    return HEADER + r.tobytes() + TRAILER


def writer(dsn, q, counters, base):
    """Thread: takes (N, RECSZ) uint8 batches from q, validates, COPYs into PostgreSQL."""
    loop = asyncio.new_event_loop()
    conn = None
    while True:
        arr = q.get()
        if arr is None:
            break
        rec = arr.view(IN).reshape(-1)
        ok = (rec["magic"] == MAGIC) & (rec["ver"] == VERSION)
        bad = len(rec) - int(ok.sum())
        if bad:
            counters[base + BADMAGIC] += bad
            rec = rec[ok]
        if len(rec) == 0:
            continue

        if not dsn:                                 # test mode: discard
            counters[base + WRITTEN] += len(rec)
            continue

        import asyncpg
        data = to_copy_bytes(rec)
        for attempt in range(4):
            try:
                if conn is None:
                    conn = loop.run_until_complete(asyncpg.connect(dsn))
                loop.run_until_complete(conn.copy_to_table(
                    "readings", source=io.BytesIO(data), format="binary", columns=COLUMNS))
                counters[base + WRITTEN] += len(rec)
                break
            except Exception as e:
                log.warning("DB write failed (attempt %d): %s", attempt + 1, e)
                if conn is not None:
                    try:
                        loop.run_until_complete(conn.close())
                    except Exception:
                        pass
                    conn = None
                time.sleep(min(2 ** attempt, 5))
        else:
            counters[base + FAILED] += len(rec)
            log.error("giving up on a batch of %d rows", len(rec))

    if conn is not None:
        loop.run_until_complete(conn.close())


# ---------------------------------------------------------------- receiver
def receiver(idx, args, counters):
    base = idx * NSLOT
    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    signal.signal(signal.SIGTERM, lambda *_: stop.set())

    libc = load_libc()
    libc.recvmmsg.argtypes = [c_int, POINTER(mmsghdr), c_uint, c_int, c_void_p]
    libc.recvmmsg.restype = c_int
    recvmmsg = libc.recvmmsg

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, args.rcvbuf)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, struct.pack("@ll", 1, 0))
    sock.bind((args.host, args.port))
    fd = sock.fileno()
    log.info("rx%d listening on %s:%d (rcvbuf effective=%d)", idx, args.host, args.port,
             sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))

    vlen = args.vlen
    rbuf = np.zeros((vlen, RECSZ), dtype=np.uint8)       # kernel writes packets here
    rbase = rbuf.ctypes.data
    iovs = (iovec * vlen)()
    msgs = (mmsghdr * vlen)()
    for i in range(vlen):
        iovs[i].iov_base = rbase + i * RECSZ
        iovs[i].iov_len = RECSZ
        h = msgs[i].msg_hdr
        h.msg_name = None
        h.msg_namelen = 0
        h.msg_iov = ctypes.pointer(iovs[i])
        h.msg_iovlen = 1
    # numpy view of every msg_len field, to detect packets that are not RECSZ bytes
    lens = np.frombuffer(msgs, dtype=np.dtype({
        "names": ["len"], "formats": ["=u4"],
        "offsets": [mmsghdr.msg_len.offset], "itemsize": ctypes.sizeof(mmsghdr)}))["len"]

    acc = np.empty((args.batch + vlen, RECSZ), dtype=np.uint8)   # accumulates a DB batch
    n_acc = 0
    q = queue.Queue(maxsize=args.queue_batches)
    wt = threading.Thread(target=writer, args=(args.db_url, q, counters, base), daemon=True)
    wt.start()

    recv = badlen = dropped = 0
    last_flush = last_pub = time.monotonic()

    def flush():
        nonlocal n_acc, dropped
        if n_acc == 0:
            return
        try:
            q.put_nowait(acc[:n_acc].copy())
        except queue.Full:                  # DB too slow: drop, never stall receiving
            dropped += n_acc
        n_acc = 0

    while not stop.is_set():
        n = recvmmsg(fd, msgs, vlen, MSG_WAITFORONE, None)
        if n < 0:
            err = ctypes.get_errno()
            if err not in (EINTR, EAGAIN):
                raise OSError(err, os.strerror(err))
            n = 0
        if n:
            recv += n
            good = lens[:n] == RECSZ
            if good.all():
                acc[n_acc:n_acc + n] = rbuf[:n]
                n_acc += n
            else:
                k = int(good.sum())
                badlen += n - k
                if k:
                    acc[n_acc:n_acc + k] = rbuf[:n][good]
                    n_acc += k

        now = time.monotonic()
        if n_acc >= args.batch or (n_acc and now - last_flush >= args.flush):
            flush()
            last_flush = now
        if now - last_pub >= 0.5:
            counters[base + RECV] = recv
            counters[base + BADLEN] = badlen
            counters[base + DROPPED] = dropped
            last_pub = now

    flush()                                 # graceful shutdown: write what is left
    q.put(None)
    wt.join(timeout=30)
    counters[base + RECV] = recv
    counters[base + BADLEN] = badlen
    counters[base + DROPPED] = dropped
    log.info("rx%d stopped", idx)


# -------------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=9999)
    p.add_argument("--procs", type=int, default=min(4, os.cpu_count() or 1))
    p.add_argument("--vlen", type=int, default=128, help="packets per recvmmsg call")
    p.add_argument("--rcvbuf", type=int, default=64 * 1024 * 1024)
    p.add_argument("--batch", type=int, default=50000, help="rows per DB COPY")
    p.add_argument("--flush", type=float, default=0.5, help="max seconds before a partial batch is written")
    p.add_argument("--queue-batches", type=int, default=32, help="writer queue depth per process")
    p.add_argument("--db-url", default=None, help="omit for test mode (no database)")
    p.add_argument("--unlogged", action="store_true",
                   help="create table UNLOGGED (faster, but data is lost if PostgreSQL crashes)")
    args = p.parse_args()

    if args.db_url:
        asyncio.run(init_schema(args.db_url, args.unlogged))
        log.info("database ready")
    else:
        log.warning("no --db-url: TEST MODE, data is discarded")

    counters = mp.Array("Q", args.procs * NSLOT, lock=False)
    procs = [mp.Process(target=receiver, args=(i, args, counters)) for i in range(args.procs)]
    for pr in procs:
        pr.start()

    def total(slot):
        return sum(counters[i * NSLOT + slot] for i in range(args.procs))

    prev = 0
    try:
        while any(pr.is_alive() for pr in procs):
            time.sleep(1)
            r = total(RECV)
            log.info("recv/s=%d total=%d badlen=%d badmagic=%d dropped=%d written=%d failed=%d",
                     r - prev, r, total(BADLEN), total(BADMAGIC), total(DROPPED),
                     total(WRITTEN), total(FAILED))
            prev = r
    except KeyboardInterrupt:
        pass
    finally:
        for pr in procs:
            if pr.is_alive():
                pr.terminate()
        for pr in procs:
            pr.join(timeout=40)
        log.info("FINAL recv=%d badlen=%d badmagic=%d dropped=%d written=%d failed=%d",
                 total(RECV), total(BADLEN), total(BADMAGIC), total(DROPPED),
                 total(WRITTEN), total(FAILED))


if __name__ == "__main__":
    main()
