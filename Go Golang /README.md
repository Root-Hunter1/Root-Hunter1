# Go Golang Examples

This folder contains standalone Go learning exercises and small server experiments. The examples introduce Go fundamentals, concurrency, networking, interfaces, and structs through simple programs.

> These are educational examples, not production-ready security or networking tools. Some files currently contain syntax or implementation issues and may need fixes before they compile or run correctly.

## Requirements

- Go installed and available on your `PATH` (`go version`)
- A terminal

## Examples in This Folder

| File | What it demonstrates |
| --- | --- |
| `Channel` | Creates a channel, starts a goroutine, and waits for a message from it. |
| `DNS server` | Demonstrates domain filtering with a map and simple string checks. It uses a hard-coded example domain. |
| `GO-LANG IF-ELSE LAB ACTIVE` | Shows conditional branching (`if`, `else if`, and `else`) with sample IP values. |
| `Goroutine` | Starts several goroutines to illustrate concurrent function execution. |
| `Http server` | Registers an HTTP handler and serves a plain-text response on port `8080`. |
| `Interface` | Demonstrates an interface implemented by two example filter types. |
| `Pointer` | Shows a function that checks a sample IP and returns a decision message. |
| `Project DNS Server` | Demonstrates receiving and replying to UDP packets on port `8053`; it uses a simulated domain rather than parsing DNS messages. |
| `Struc Engine` | Defines a struct and method to demonstrate organizing server-like configuration and behavior. |

## Running an Example

The files are standalone programs without `.go` extensions. Run one file at a time from the repository root, quoting paths because the directory name contains spaces:

```bash
go run "Go Golang /Channel"
go run "Go Golang /DNS server"
go run "Go Golang /Http server"
```

For the HTTP server, visit `http://localhost:8080` after it starts. For the UDP example, it listens on port `8053`. Stop a running server with `Ctrl+C`.

Each file declares `package main`, so these examples should not be built together as a single package without first restructuring them (for example, into separate subdirectories).

## Important Notes

- Some source files appear to have compile-time errors, including misspelled Go identifiers and Python-style expressions. Review and fix a file before running it if `go run` reports errors.
- The examples use hard-coded IP addresses and domain names; they do not implement a real firewall, content filter, or complete DNS server.
- Some programs execute the `clear` command, which is not available by default on every operating system.
- Do not expose the sample servers to untrusted networks or rely on them for security decisions.

These programs are provided for learning and experimentation with Go.
