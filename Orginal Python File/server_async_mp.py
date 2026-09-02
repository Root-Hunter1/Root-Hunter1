#!/usr/bin/env python3
"""
Asyncio + Multiprocessing hybrid UDP server.

- asyncio in the main process receives datagrams (non-blocking).
- Received (bytes, addr) are enqueued into a multiprocessing.Queue.
- Worker processes read from the queue, do CPU-bound work, and send replies
  using their own UDP socket.

Run: python3 server_async_mp.py --host 0.0.0.0 --port 9999 --workers 4
"""
import asyncio
import multiprocessing as mp
import socket
import time
import signal
import sys
import argparse
import queue as _queue  # for Full exception type
from typing import Tuple

HOST = "0.0.0.0"
PORT = 9999
WORKER_COUNT = 4
QUEUE_MAXSIZE = 100


def worker_loop(task_queue: mp.Queue, worker_id: int):
    """Worker process: receives (data, addr) from the queue, processes it, and replies."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # allow reuse if needed (not binding same addr here)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    pid = mp.current_process().pid
    print(f"[worker-{worker_id}] started (pid={pid})")

    try:
        while True:
            item = task_queue.get()
            if item is None:
                print(f"[worker-{worker_id}] received shutdown sentinel")
                break

            data, addr = item
            # Example CPU-bound processing (replace with real work)
            start = time.perf_counter()
            s = 0
            for i in range(50000):
                s += i * i
            duration = time.perf_counter() - start

            resp = (
                f"worker={worker_id} pid={pid} processed_bytes={len(data)} cpu_ms={int(duration*1000)}"
            ).encode("utf-8")
            try:
                sock.sendto(resp, addr)
            except Exception as e:
                print(f"[worker-{worker_id}] failed to send to {addr}: {e}")
    finally:
        sock.close()
        print(f"[worker-{worker_id}] exiting")


class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, task_queue: mp.Queue, queue_maxsize: int):
        self.task_queue = task_queue
        self.queue_maxsize = queue_maxsize
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        sock = transport.get_extra_info("socket")
        addr = sock.getsockname() if sock is not None else ("?", "?")
        print(f"[main] UDP socket ready on {addr}")

    def datagram_received(self, data: bytes, addr):
        # datagram_received runs in the event loop thread, so keep it very fast.
        try:
            # copy data to ensure worker gets immutable bytes (asyncio may reuse buffer)
            self.task_queue.put_nowait((bytes(data), addr))
        except _queue.Full:
            # backpressure: reject packet quickly
            print(f"[main] task queue full; dropping packet from {addr}")
            try:
                if self.transport:
                    self.transport.sendto(b"server-busy", addr)
            except Exception:
                pass

    def error_received(self, exc):
        print(f"[main] socket error: {exc}")

    def connection_lost(self, exc):
        print("[main] transport closed")


async def run_server(host: str, port: int, workers: int, queue_maxsize: int):
    """Start workers and run asyncio datagram endpoint."""
    # Start worker processes
    mp.set_start_method("spawn", force=True)  # safe default for macOS/Windows
    task_queue: mp.Queue = mp.Queue(maxsize=queue_maxsize)

    procs = []
    for i in range(workers):
        p = mp.Process(target=worker_loop, args=(task_queue, i + 1), daemon=False)
        p.start()
        procs.append(p)

    loop = asyncio.get_running_loop()

    # Create datagram endpoint bound to (host, port)
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPProtocol(task_queue, queue_maxsize),
        local_addr=(host, port),
    )

    shutdown_event = asyncio.Event()

    def _on_signal():
        print("\n[main] shutdown signal received (async)")
        shutdown_event.set()

    # register signal handlers (Unix); on Windows only SIGINT works
    try:
        loop.add_signal_handler(signal.SIGINT, _on_signal)
        loop.add_signal_handler(signal.SIGTERM, _on_signal)
    except NotImplementedError:
        # add_signal_handler may not be implemented on some platforms (e.g., Windows with ProactorEventLoop)
        pass

    print(f"[main] asyncio UDP server running on {host}:{port} (workers={workers})")

    # wait until signal
    await shutdown_event.wait()

    # Begin shutdown
    print("[main] closing transport...")
    transport.close()

    print("[main] sending shutdown sentinels to workers...")
    for _ in procs:
        try:
            task_queue.put_nowait(None)
        except _queue.Full:
            # If queue is full, block briefly to ensure sentinels are enqueued
            task_queue.put(None)

    # join workers
    for p in procs:
        p.join(timeout=5)
        if p.is_alive():
            print(f"[main] worker pid={p.pid} did not exit in time; terminating")
            p.terminate()

    print("[main] server stopped")


def main():
    parser = argparse.ArgumentParser(description="Asyncio + Multiprocessing UDP server")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--workers", type=int, default=WORKER_COUNT)
    parser.add_argument("--queue-size", type=int, default=QUEUE_MAXSIZE)
    args = parser.parse_args()

    try:
        asyncio.run(run_server(args.host, args.port, args.workers, args.queue_size))
    except KeyboardInterrupt:
        # fallback if signal handling didn't run
        print("\n[main] KeyboardInterrupt received; exiting")
        try:
            sys.exit(0)
        except SystemExit:
            pass


if __name__ == "__main__":
    main()
