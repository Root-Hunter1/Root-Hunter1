# Copyright (C) 2026 Root-Hunter1
# Licensed under the GNU General Public License v3 (GPL-3.0-only). See LICENSE.

#!/usr/bin/env python3
"""
High-quality multiprocessing supervisor + worker pool.

Features:
- Supervisor that launches N worker processes reading from a task queue.
- Restart-on-crash with exponential backoff per-worker.
- Graceful shutdown via sentinel or signals.
- Optional heartbeat reporting & health checks.
- Central rotating-file logging. Workers inherit logger config.
- Example CPU-bound worker and UDP worker scaffold at bottom.

Usage:
- Import Supervisor and call .start() .submit_task(...) .stop()
- Or run as script to test demo_cpu.

Important:
- Tasks (callables) must be picklable (module-level functions or callable classes).
- Uses 'spawn' start method for cross-platform safety.
"""
from __future__ import annotations
import multiprocessing as mp
import time
import os
import signal
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, Any, Optional, List, Dict, Tuple

# ---------------------------------------------------------------------
# Logging setup (module-level so subprocesses inherit handler references)
# ---------------------------------------------------------------------
def setup_logging(log_path: Path = Path("logs/supervisor.log"), level=logging.INFO):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(str(log_path), maxBytes=10 * 1024 * 1024, backupCount=5)
    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(processName)s:%(process)d] %(message)s")
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(level)
    # avoid duplicate handlers
    if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == handler.baseFilename for h in root.handlers):
        root.addHandler(handler)

# ---------------------------------------------------------------------
# Worker process function wrapper
# ---------------------------------------------------------------------
def _worker_main(task_queue: mp.Queue,
                 control_queue: mp.Queue,
                 worker_id: int,
                 task_fn: Callable[[Any], Any],
                 init_args: Tuple = (),
                 heartbeat_interval: float = 5.0):
    """
    Worker process: pulls tasks from task_queue, calls task_fn(task), optionally reports
    simple heartbeats to control_queue as ("hb", worker_id, timestamp).
    Cleanly exits on sentinel (None).
    """
    logger = logging.getLogger(f"worker-{worker_id}")
    logger.info("worker starting (pid=%d)", os.getpid())
    last_hb = time.time()
    try:
        while True:
            try:
                task = task_queue.get(timeout=heartbeat_interval)
            except Exception:
                # timed out waiting for task -> send heartbeat if needed and loop
                now = time.time()
                if now - last_hb >= heartbeat_interval:
                    try:
                        control_queue.put(("hb", worker_id, now))
                    except Exception:
                        pass
                    last_hb = now
                continue

            # sentinel to exit
            if task is None:
                logger.info("worker received shutdown sentinel")
                break

            # task is a (task_id, payload) pair optionally; adapt as you want
            try:
                task_id, payload = task if isinstance(task, tuple) and len(task) == 2 else (None, task)
                start = time.time()
                result = task_fn(payload, *init_args) if init_args else task_fn(payload)
                duration = time.time() - start
                logger.info("task done id=%s duration=%.3fs", task_id, duration)
                # report completion
                try:
                    control_queue.put(("done", worker_id, task_id, duration))
                except Exception:
                    pass
            except Exception as e:
                logger.exception("task raised exception: %s", e)
                try:
                    control_queue.put(("err", worker_id, task_id, str(e)))
                except Exception:
                    pass
    except KeyboardInterrupt:
        logger.info("worker interrupted by KeyboardInterrupt")
    except Exception:
        logger.exception("worker fatal error")
    finally:
        logger.info("worker exiting")

# ---------------------------------------------------------------------
# Supervisor class
# ---------------------------------------------------------------------
class Supervisor:
    def __init__(self,
                 num_workers: int,
                 task_fn: Callable[[Any], Any],
                 *,
                 init_args: Tuple = (),
                 queue_maxsize: int = 1000,
                 heartbeat_interval: float = 5.0,
                 log_path: Path = Path("logs/supervisor.log")):
        """
        Create Supervisor.

        - num_workers: desired worker count
        - task_fn: picklable callable executed in workers; must accept a single argument (payload)
        - init_args: optional tuple passed to task_fn on each call after payload
        - queue_maxsize: task queue maxsize
        - heartbeat_interval: used by worker to send heartbeats
        """
        mp.set_start_method("spawn", force=False)  # safe default; force=False to avoid re-setting
        setup_logging(log_path)
        self.logger = logging.getLogger("supervisor")
        self.num_workers = int(num_workers)
        self.task_fn = task_fn
        self.init_args = init_args
        self.queue_maxsize = queue_maxsize
        self.heartbeat_interval = heartbeat_interval

        # queues for tasks and control messages from workers
        ctx = mp.get_context("spawn")
        self.task_queue: mp.Queue = ctx.Queue(maxsize=self.queue_maxsize)
        self.control_queue: mp.Queue = ctx.Queue()
        self.workers: List[mp.Process] = []
        # restart/backoff state per worker index
        self._backoffs: Dict[int, float] = {}
        self._started_at: Dict[int, float] = {}
        self._running = False

    def start(self):
        self.logger.info("supervisor starting %d workers", self.num_workers)
        self._running = True
        for i in range(self.num_workers):
            self._start_worker(i)

        # install signal handlers for graceful termination in parent
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # monitoring loop runs in a separate thread to avoid blocking caller if desired
        self._monitor_thread = mp.get_context("spawn").Process  # placeholder: we'll use simple loop in main thread
        # For simple usage, user calls supervise() which runs a blocking monitor loop.

    def _start_worker(self, idx: int):
        """Start a worker process at index idx."""
        backoff = self._backoffs.get(idx, 1.0)
        if backoff > 1.0:
            self.logger.info("backoff for worker %d = %.1fs (sleeping before restart)", idx, backoff)
            time.sleep(backoff)
        ctx = mp.get_context("spawn")
        p = ctx.Process(target=_worker_main,
                        args=(self.task_queue, self.control_queue, idx, self.task_fn, self.init_args, self.heartbeat_interval),
                        name=f"worker-{idx}")
        p.daemon = False
        p.start()
        self.workers.append(p)
        self._started_at[idx] = time.time()
        # reset backoff if worker stays alive enough
        self._backoffs[idx] = 1.0
        self.logger.info("started worker idx=%d pid=%d", idx, p.pid)

    def submit_task(self, payload: Any, task_id: Optional[str] = None, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Submit a task to queue. payload can be any picklable object.
        If task_id provided, it will be sent as (task_id, payload).
        Returns True if enqueued, False on full queue (non-blocking).
        """
        item = (task_id, payload) if task_id is not None else payload
        try:
            self.task_queue.put(item, block=block, timeout=timeout)
            return True
        except Exception:
            return False

    def supervise(self, poll_interval: float = 1.0):
        """
        Blocking monitor loop: checks control_queue for messages and restarts dead workers.
        Call this after start() to run the supervisor loop. Use stop() to exit.
        """
        self.logger.info("entering supervise loop")
        try:
            while self._running:
                # process control messages
                try:
                    msg = self.control_queue.get(timeout=poll_interval)
                except Exception:
                    msg = None

                if msg:
                    self._handle_control(msg)

                # check worker liveness and restart if needed
                for idx, p in list(enumerate(self.workers)):
                    if not p.is_alive():
                        rc = p.exitcode
                        self.logger.warning("worker idx=%d pid=%s exited rc=%s", idx, getattr(p, "pid", None), rc)
                        # remove from list
                        try:
                            self.workers.remove(p)
                        except ValueError:
                            pass
                        # restart with exponential backoff
                        prev = self._backoffs.get(idx, 1.0)
                        new_backoff = min(prev * 2.0, 30.0)
                        self._backoffs[idx] = new_backoff
                        self.logger.info("scheduling restart of worker %d with backoff %.1f", idx, new_backoff)
                        self._start_worker(idx)
                # small sleep to avoid busy loop
        except KeyboardInterrupt:
            self.logger.info("supervisor interrupted by user")
            self.stop()
        except Exception:
            self.logger.exception("supervisor encountered fatal error; stopping")
            self.stop()

    def _handle_control(self, msg):
        # examples of messages: ("hb", worker_id, ts), ("done", worker_id, task_id, duration)
        typ = msg[0]
        if typ == "hb":
            _, wid, ts = msg
            self.logger.debug("heartbeat from worker %d @ %.1f", wid, ts)
        elif typ == "done":
            _, wid, task_id, duration = msg
            self.logger.info("worker %d completed task %s in %.3fs", wid, task_id, duration)
        elif typ == "err":
            _, wid, task_id, err = msg
            self.logger.warning("worker %d task %s error: %s", wid, task_id, err)
        else:
            self.logger.debug("unknown control msg: %r", msg)

    def stop(self, graceful: bool = True, timeout: float = 5.0):
        """
        Stop supervisor and workers.
        - If graceful, send sentinel None to each worker (they exit cleanly).
        - If not graceful, terminate processes.
        """
        self.logger.info("supervisor stopping (graceful=%s)", graceful)
        self._running = False
        if graceful:
            # send one sentinel per live worker
            for _ in range(len(self.workers)):
                try:
                    self.task_queue.put_nowait(None)
                except Exception:
                    try:
                        self.task_queue.put(None, timeout=1.0)
                    except Exception:
                        pass
            # wait for workers to exit
            deadline = time.time() + timeout
            for p in list(self.workers):
                remaining = max(0.0, deadline - time.time())
                try:
                    p.join(timeout=remaining)
                except Exception:
                    pass
                if p.is_alive():
                    self.logger.warning("worker pid=%s did not exit in time; terminating", p.pid)
                    try:
                        p.terminate()
                    except Exception:
                        pass
        else:
            for p in list(self.workers):
                try:
                    p.terminate()
                except Exception:
                    pass
        # final join & cleanup
        for p in list(self.workers):
            try:
                p.join(timeout=1.0)
            except Exception:
                pass
        self.workers.clear()
        self.logger.info("supervisor stopped")

# ---------------------------------------------------------------------
# Demo task functions (must be module-level to be picklable)
# ---------------------------------------------------------------------
def cpu_heavy_task(n: int) -> int:
    """Simple CPU-bound: sum of squares up to n"""
    total = 0
    for i in range(n):
        total += i * i
    return total

# Note: UDP worker example is only a scaffold. For real UDP server design use queue + worker sockets as shown earlier.
def udp_echo_task(payload: Tuple[bytes, Tuple[str, int]], *args) -> bytes:
    """
    payload: (data, (host, port))
    This function demonstrates processing; in real use you would send reply via socket.
    """
    data, addr = payload
    # pretend to process and echo back
    return b"ACK:" + data[:128]

# ---------------------------------------------------------------------
# Simple command-line demo
# ---------------------------------------------------------------------
def demo_cpu():
    sup = Supervisor(num_workers=4, task_fn=lambda x: cpu_heavy_task(x), init_args=())
    sup.start()
    # submit 20 tasks
    for i in range(20):
        sup.submit_task((f"task-{i}", 200_000), task_id=f"task-{i}")
    # run supervisor loop for a while
    try:
        start = time.time()
        while time.time() - start < 10:
            sup.supervise(poll_interval=1.0)
            break  # supervise is blocking; we call once for demo
    except KeyboardInterrupt:
        pass
    finally:
        sup.stop(graceful=True)

if __name__ == "__main__":
    # small run when executed directly
    print("This module provides Supervisor for multiprocessing. Import and use in your app.")
    # Uncomment following to run demo quickly:
    # demo_cpu()
