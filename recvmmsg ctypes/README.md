# Linux UDP Batch I/O Experiments with Python `ctypes`

This folder contains learning experiments that call Linux's `sendmmsg()` and `recvmmsg()` system interfaces from Python using `ctypes`. The scripts explore batched UDP I/O, multiprocessing, socket buffers, and packet-rate measurement.

These are low-level networking and load-testing examples—not production servers or general-purpose DNS tools. Use them only on a machine and network you own or have explicit permission to test. Keep experiments isolated and bounded; high-rate UDP traffic can disrupt networks and services.

## Contents

| File | Description |
| --- | --- |
| `send.py` | Multi-process UDP sender using `sendmmsg()`. It accepts a destination host and port, packet size, batch length, process/socket counts, and duration, and prints send-rate and total counters. The default destination is loopback (`127.0.0.1`). |
| `python mm.py 8` | Multi-process UDP receiver using `recvmmsg()`. It binds UDP sockets on port `9999`, receives batches, and reports receive counts per second. The filename includes a space; the trailing `8` in the filename is not a required argument. |
| `udp_pg.py` | PostgreSQL-oriented UDP ingestion experiment, as indicated by its companion notes. Review its source and database configuration before use. |
| `udp_pg.py Redme` | Short notes with example PostgreSQL inspection and launch commands. Check these instructions against the script before using them. |
| `Redme.md` | Earlier notes on sender tuning and selecting a libc name for different environments. |
| `Sender/` | A directory present in the repository; no files were listed when this README was written. |

## Platform and Dependencies

- Python 3
- Linux with a compatible C library exposing `sendmmsg()` and/or `recvmmsg()`
- PostgreSQL and a suitable Python PostgreSQL driver may be needed for `udp_pg.py`; inspect its imports and arguments

The scripts use only Python's standard-library modules for their `ctypes`, socket, multiprocessing, and timing logic. The `mmsg` interfaces and the shown C structure layouts are platform/ABI-specific; they should not be assumed to work on Windows, macOS, or every Linux/Android environment. The existing notes mention `libc.so` for some mobile environments, but compatibility must be verified on the actual device.

## Safety and Operational Notes

- Keep the sender pointed at loopback or a controlled test receiver. Do not direct it at public or third-party hosts.
- The sender's process, socket, batch, payload-size, and duration options can significantly change traffic volume. Do not increase them without understanding the impact and setting strict limits.
- The receiver binds to `0.0.0.0:9999`, making the port reachable on available network interfaces. Restrict access with host/network firewall rules and stop the process when testing is complete.
- UDP does not guarantee delivery. Compare sender and receiver counts; differences can reflect packet loss, buffering, scheduling, or measurement behavior.
- The receiver's shared counter is periodically updated, and the script is designed as a measurement experiment rather than a durable service. It runs continuously until stopped.
- The scripts use `ctypes` to call C functions directly. Incorrect structure definitions, argument types, or platform assumptions can cause errors or process crashes.
- `udp_pg.py` may write data to a database. Review its database URL, schema, and cleanup behavior before running it; do not use destructive SQL against data you need.

## Learning Goals

- Understand batched datagram system calls and how they differ from one-call-per-packet loops.
- Explore Python-to-C interfaces with `ctypes` and C-compatible structures.
- Observe multiprocessing and UDP socket-buffer behavior under controlled conditions.
- Treat throughput results as local experiments, not as production capacity claims.

Inspect each script and its command-line help/source before running it. These examples are educational and are not intended for benchmarking or traffic generation against systems without explicit authorization.
