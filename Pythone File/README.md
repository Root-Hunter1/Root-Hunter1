# Python Learning Examples

This folder contains standalone Python exercises covering networking, concurrency, file operations, object-oriented programming, and utility scripts. These are educational experiments, not production-ready tools.

## Requirements

- Python 3
- Optional third-party packages, depending on the example:
  - `requests` — HTTP client, web crawler, and the password-guessing demonstration
  - `beautifulsoup4` — HTML parsing in the web link crawler
  - `dnspython` — DNS record lookup example
  - `paramiko` — SSH client example

Install optional dependencies as needed:

```bash
python -m pip install requests beautifulsoup4 dnspython paramiko
```

## Examples

Most files do not have a `.py` extension. Run a selected script from the repository root with its quoted path, for example:

```bash
python "Pythone File/Password Genarato"
```

| File | Purpose |
| --- | --- |
| `Asyncio Engine` | Demonstrates an asyncio UDP datagram endpoint and asynchronous packet-handling tasks. Its response is a sample payload, not a standards-compliant DNS reply. |
| `Banner Graper` | A socket programming exercise that connects to a user-specified host and port and displays the returned service banner. Use only with systems you own or are authorized to test. |
| `Brute Froce` | An unsafe password-guessing demonstration that sends HTTP requests to a hard-coded external target. Do not run it against real services; it is included only as code for security-awareness review. |
| `Chat = Application 2` | A TCP chat client that connects to a server, receives messages on a background thread, and sends user-entered messages. |
| `Chat Application` | A simple TCP chat server that accepts one client and exchanges text messages interactively. |
| `Class OOP` | Demonstrates classes, UDP sockets, and threading with a small server-like example. |
| `DNS Lookup Engine or DNS Resolver` | An attempted DNS lookup exercise for address and DNS record types. The current file has syntax and name errors and requires correction before it can run. |
| `DNS chach` | Demonstrates a dictionary-based DNS cache, system name resolution on a cache miss, and a simulated cache-poisoning check. |
| `File Handaling` | Creates and scans a sample log file, then removes it when matching lines are found. The current file contains a syntax error; review it before running. |
| `File Manager Engine.py` | An interactive example for listing, creating, renaming, and deleting files or directories in the current working directory. Deletion is permanent, so use care. |
| `Http client` | Demonstrates making an HTTP GET request and displaying selected response metadata. The current file contains a syntax error; review it before running. |
| `Http server` | A minimal socket-based HTTP server bound to localhost on port `8080`. |
| `Mac Address Changer.py` | A Linux-specific system administration experiment that attempts to change a network interface's MAC address. It requires elevated privileges and can disrupt connectivity; use only on your own device. |
| `New Http Server2` | Uses Python's standard-library HTTP server to serve a generated `index.html` file on port `8080`. |
| `Password Genarato` | An interactive password generator with selectable character groups and a basic strength indicator. It uses Python's `random` module and should not be treated as a cryptographically secure password generator. |
| `SSH Engine` | Demonstrates an SSH connection and remote command execution using Paramiko. It uses placeholder credentials and an unsafe automatic host-key policy; do not use as-is. |
| `Threading  Use..` | An attempted threaded UDP/DNS server exercise. The current file contains naming and implementation errors and requires correction before it can run. |
| `Web Link Crawler` | Fetches a supplied page and extracts anchor links using Requests and Beautiful Soup. Crawl only sites you are authorized to access and respect their policies. |
| `multiprocessing` | Demonstrates starting and joining separate processes and measuring elapsed time. The example tasks simulate work with a delay. |

## Running Network Examples Safely

Several examples bind local services to ports such as `5000`, `5353`, `8080`, and `9999`, or connect to a host supplied in code or at the prompt. Run them only in a controlled environment and use systems you own or have explicit permission to test. Stop server processes with `Ctrl+C`.

## Known Limitations

- Some files currently contain syntax errors, misspelled names, or incomplete logic. Python may report errors before an example starts; inspect and fix the relevant script first.
- Several scripts call `clear`, which may not work on Windows. The file manager and MAC changer can modify or remove local system data.
- The network examples are learning exercises. They do not provide production-grade DNS, HTTP, SSH, or security functionality.
- Review scripts before running them, especially those that perform network requests, execute remote commands, change network settings, or delete files.
