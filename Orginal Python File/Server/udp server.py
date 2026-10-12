#!/usr/bin/env python3
"""
High-speed asyncio UDP server (multi-process + batching)
"""
import argparse
import asyncio
import logging
import multiprocessing as mp
import signal
import socket
import time

from database import Database

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("udp")

BATCH_SIZE = 500
BATCH_TIMEOUT = 0.05


class Stats:
    __slots__ = ("recv", "processed", "dropped", "errors", "bytes_recv")

    def __init__(self):
        self.recv = self.processed = self.dropped = self.errors = self.bytes_recv = 0


class UDPProtocol(asyncio.DatagramProtocol):
    __slots__ = ("queue", "stats", "transport")

    def __init__(self, queue, stats):
        self.queue = queue
        self.stats = stats
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        s = self.stats
        s.recv += 1
        s.bytes_recv += len(data)
        try:
            self.queue.put_nowait((data, addr))
        except asyncio.QueueFull:
            s.dropped += 1

    def error_received(self, exc):
        self.stats.errors += 1


def process(data: bytes):
    # আপনার আসল লজিক এখানে (পার্স + ভ্যালিডেট)
    return data


async def worker(queue, protocol, stats, db_queue, send_reply):
    while True:
        try:
            # একটা আইটেমের জন্য অপেক্ষা, তারপর যা জমেছে সব একসাথে নাও
            batch = [await queue.get()]
            while not queue.empty() and len(batch) < BATCH_SIZE:
                batch.append(queue.get_nowait())
        except asyncio.CancelledError:
            break

        try:
            rows = []
            for data, addr in batch:
                result = process(data)
                rows.append((addr[0], addr[1], result))
                if send_reply:
                    protocol.transport.sendto(b"OK", addr)

            try:
                db_queue.put_nowait(rows)
            except asyncio.QueueFull:
                stats.dropped += len(rows)

            stats.processed += len(batch)
        except Exception:
            stats.errors += 1
            log.exception("worker error")
        finally:
            for _ in batch:
                queue.task_done()


async def db_writer(db_queue, database):
    while True:
        try:
            rows = await db_queue.get()
        except asyncio.CancelledError:
            return

        # আরও জমা থাকলে একসাথে মিলিয়ে নাও
        while not db_queue.empty() and len(rows) < BATCH_SIZE * 4:
            rows.extend(db_queue.get_nowait())
            db_queue.task_done()

        try:
            await database.insert_many(rows)
        except Exception:
            log.exception("db write failed (%d rows)", len(rows))
        finally:
            db_queue.task_done()


async def stats_reporter(queue, stats, interval, pid):
    prev_recv = prev_proc = 0
    while True:
        await asyncio.sleep(interval)
        rr = (stats.recv - prev_recv) / interval
        pr = (stats.processed - prev_proc) / interval
        prev_recv, prev_proc = stats.recv, stats.processed
        log.info("[pid %d] recv/s=%.0f proc/s=%.0f dropped=%d errors=%d queue=%d",
                 pid, rr, pr, stats.dropped, stats.errors, queue.qsize())


def build_socket(host, port, buf):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)   # মাল্টি-প্রসেসের জন্য জরুরি
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buf)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buf)
    sock.setblocking(False)
    sock.bind((host, port))
    return sock


async def serve(args):
    import os
    loop = asyncio.get_running_loop()
    stats = Stats()
    queue = asyncio.Queue(maxsize=args.queue)
    db_queue = asyncio.Queue(maxsize=1000)
    stop = asyncio.Event()

    database = Database(args.db_url, max_size=4)
    await database.connect()

    sock = build_socket(args.host, args.port, args.recv_buf)
    protocol = UDPProtocol(queue, stats)
    transport, _ = await loop.create_datagram_endpoint(lambda: protocol, sock=sock)

    workers = [asyncio.create_task(worker(queue, protocol, stats, db_queue, args.reply))
               for _ in range(args.workers)]
    writer = asyncio.create_task(db_writer(db_queue, database))
    reporter = asyncio.create_task(stats_reporter(queue, stats, 5.0, os.getpid()))

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    await stop.wait()

    transport.close()
    try:
        await asyncio.wait_for(queue.join(), timeout=5)
        await asyncio.wait_for(db_queue.join(), timeout=5)
    except asyncio.TimeoutError:
        log.warning("drain timeout")

    for t in (*workers, writer, reporter):
        t.cancel()
    await asyncio.gather(*workers, writer, reporter, return_exceptions=True)
    await database.close()


def run_process(args):
    try:
        import uvloop
        uvloop.run(serve(args))
    except ImportError:
        asyncio.run(serve(args))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=9999)
    p.add_argument("--procs", type=int, default=mp.cpu_count(), help="প্রসেস সংখ্যা")
    p.add_argument("--workers", type=int, default=2, help="প্রতি প্রসেসে ওয়ার্কার")
    p.add_argument("--queue", type=int, default=50000)
    p.add_argument("--recv-buf", type=int, default=8 * 1024 * 1024)
    p.add_argument("--reply", action="store_true", help="প্রতি প্যাকেটে OK রিপ্লাই পাঠাও")
    p.add_argument("--db-url", type=str)
    args = p.parse_args()

    procs = [mp.Process(target=run_process, args=(args,)) for _ in range(args.procs)]
    for pr in procs:
        pr.start()
    try:
        for pr in procs:
            pr.join()
    except KeyboardInterrupt:
        for pr in procs:
            pr.terminate()


if __name__ == "__main__":
    main()
