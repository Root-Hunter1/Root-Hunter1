# Orginal Python File

This folder contains Python examples and experimental programs for learning and testing: calculators, DNS lookup utilities, UDP clients and servers, multiprocessing examples, and PostgreSQL integration. UDP-related files are intended for use on the local machine or in an explicitly authorized test environment. Do not test against systems or networks you do not own or have permission to test.

## File overview

| File | Purpose |
|---|---|
| `Calculator.py` | Runs a terminal calculator supporting addition, subtraction, multiplication, division, modulo, and exponentiation. It also displays calculation history for the current session. |
| `dns_lookup.py` | Uses `dnspython` to query DNS records such as A, AAAA, MX, NS, and TXT; it also supports PTR reverse lookups. |
| `client.py` | A terminal HTTP chat client that receives messages from a server and posts messages as a user. Requires `requests`. |
| `database.py` | Creates an asynchronous PostgreSQL connection pool for the UDP server and provides support for saving UDP packet data. |
| `High-performance asyncio udp v1.0` | An asyncio-based UDP server example that uses queues and workers to process datagrams, collect statistics, and integrate with PostgreSQL. |
| `asyncio_udp_v2.0_optimized` | An experimental batch/thread-pool version of an asyncio UDP server, including queues, statistics, and shutdown handling. |
| `Multiprocess Engine v2.0` | Demonstrates UDP datagram processing with multiprocessing queues and worker processes. |
| `server_async_mp.py` | Receives UDP datagrams with asyncio and forwards them to multiprocessing workers, which process packets and send responses. |
| `multiprocessing supervisor + worker pool.py` | Reusable multiprocessing example with task queues, heartbeat messages, worker restart, exponential backoff, and graceful shutdown. |
| `asyncio request sender v1.0` | A lightweight asyncio UDP sender for local throughput or latency testing. Use only with an owned or authorized test server. |
| `Multiprocess Request Sender v2.0` | Generates UDP traffic using multiple processes and threads for controlled load/performance tests against a server you own or have permission to test. |
| `Docker-compose.yml` | Draft Docker configuration for an image/container. It references `7.py`, which is not listed in this folder, so review and update the configuration before use. |
| `requirements.txt` | Lists PostgreSQL driver/pool dependencies and `uvloop` for non-Windows platforms. It may not include dependencies used by every script. |

## `Server/` subfolder

| File | Purpose |
|---|---|
| `Server/udp server.py` | An asyncio UDP server that batches packets, processes them with workers, optionally sends replies, and stores data in PostgreSQL. |
| `Server/database.py` | Uses `asyncpg` to manage a PostgreSQL pool and the `packets` table, and performs batch inserts. |
| `Server/sender.py` | Sends test datagrams to UDP port `9999` on localhost. Use it only with a local test server. |
| `Server/Redme .md` | Previous server and PostgreSQL setup notes. These may be outdated or incomplete, so verify them against the current code and dependencies. |

## Before running

- Use Python 3.
- Install `dnspython` for `dns_lookup.py` and `requests` for `client.py`.
- PostgreSQL-based servers require PostgreSQL to be running and a valid connection URL. Use `requirements.txt` for the dependencies listed there.
- The code in `Server/` uses `asyncpg`, which is not listed in the current `requirements.txt`.
- Scripts do not all use the same dependencies. Check each file's imports and command-line arguments before installing packages.
- Binding a UDP server to `0.0.0.0` exposes it to available network interfaces. For learning and testing, use localhost or an isolated test environment.

## Safe usage

These are educational and experimental examples. UDP sender and load-test scripts should only be used against systems you control or have written permission to test. Never generate traffic against a public service or third-party network without authorization.
