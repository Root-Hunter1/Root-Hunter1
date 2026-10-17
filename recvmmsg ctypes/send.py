#!/usr/bin/env python3
"""UDP load generator (sendmmsg + multi-process + multi-socket).
Use only to test your own server."""
import argparse, ctypes, ctypes.util, os, socket, time
import multiprocessing as mp
from ctypes import c_void_p, c_size_t, c_uint32, c_int, c_uint, POINTER


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


def sender(args, counter, start_at):
    libc = load_libc()
    libc.sendmmsg.argtypes = [c_int, POINTER(mmsghdr), c_uint, c_int]
    libc.sendmmsg.restype = c_int
    sendmmsg = libc.sendmmsg

    # Several sockets per process = several source ports,
    # so the kernel (SO_REUSEPORT) spreads load across all server processes
    socks = []
    for _ in range(args.socks):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, args.sndbuf)
        s.connect((args.host, args.port))
        socks.append(s)
    fds = [s.fileno() for s in socks]

    # One shared payload buffer; every slot points to it (no copying)
    payload = ctypes.create_string_buffer(b"x" * args.size, args.size)
    addr = ctypes.addressof(payload)
    iov = iovec(addr, args.size)
    msgs = (mmsghdr * args.vlen)()
    for i in range(args.vlen):
        h = msgs[i].msg_hdr
        h.msg_name = None
        h.msg_namelen = 0
        h.msg_iov = ctypes.pointer(iov)
        h.msg_iovlen = 1

    while time.time() < start_at:        # all processes start together
        pass

    end = time.monotonic() + args.duration
    sent = 0
    i = 0
    nfd = len(fds)
    vlen = args.vlen
    last = time.monotonic()
    while True:
        n = sendmmsg(fds[i % nfd], msgs, vlen, 0)
        i += 1
        if n > 0:
            sent += n
        else:
            err = ctypes.get_errno()
            if err in (4, 11, 105, 111):   # EINTR, EAGAIN, ENOBUFS, ECONNREFUSED
                continue
            raise OSError(err, os.strerror(err))

        if i % 50 == 0:                    # check the clock only occasionally
            now = time.monotonic()
            if now >= end:
                break
            if now - last >= 1.0:
                with counter.get_lock():
                    counter.value += sent
                sent = 0
                last = now

    with counter.get_lock():
        counter.value += sent


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9999)
    p.add_argument("--procs", type=int, default=3, help="sender processes")
    p.add_argument("--socks", type=int, default=4, help="sockets (source ports) per process")
    p.add_argument("--size", type=int, default=64, help="packet size in bytes")
    p.add_argument("--vlen", type=int, default=128, help="packets per syscall")
    p.add_argument("--duration", type=float, default=10.0, help="run time in seconds")
    p.add_argument("--sndbuf", type=int, default=16 * 1024 * 1024)
    args = p.parse_args()

    counter = mp.Value("Q", 0)
    start_at = time.time() + 1.0
    ps = [mp.Process(target=sender, args=(args, counter, start_at))
          for _ in range(args.procs)]
    for pr in ps:
        pr.start()

    time.sleep(1.0)
    prev = 0
    t0 = time.monotonic()
    while any(pr.is_alive() for pr in ps):
        time.sleep(1)
        cur = counter.value
        print(f"send/s = {cur - prev:,}")
        prev = cur
    for pr in ps:
        pr.join()

    total = counter.value
    el = time.monotonic() - t0
    print(f"\nTotal sent = {total:,}  (avg {total / el:,.0f} pkt/s, {args.size}B packets)")
    print("Compare this with the server's total recv. The difference is the lost packets.")


if __name__ == "__main__":
    main()
