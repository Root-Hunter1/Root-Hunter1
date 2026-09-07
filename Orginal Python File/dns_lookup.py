#!/usr/bin/env python3
"""
Terminal DNS lookup tool (async, uses dnspython).

Features:
 - Query types: A, AAAA, MX, NS, TXT, CNAME, SOA, PTR
 - Query multiple types in parallel (default)
 - Use custom DNS server(s) with --server (comma separated)
 - Timeout control
 - Reverse lookup automatically for IP when --ptr given

Requires: dnspython>=2.0
    pip install dnspython

Usage examples:
    python dns_lookup.py example.com
    python dns_lookup.py example.com --types A,MX,TXT
    python dns_lookup.py 8.8.8.8 --ptr
    python dns_lookup.py example.com --server 1.1.1.1 --timeout 3
"""
import argparse
import asyncio
import ipaddress
import sys
from typing import List

import dns.asyncresolver
import dns.exception
import dns.reversename
import dns.rdatatype

DEFAULT_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]

async def query_type(name: str, qtype: str, resolver: dns.asyncresolver.Resolver, timeout: float):
    try:
        resp = await resolver.resolve(name, qtype, lifetime=timeout)
    except dns.exception.DNSException as e:
        return qtype, None, e
    else:
        return qtype, resp, None

def format_answer(qtype: str, answer):
    lines = []
    if answer is None:
        return f"{qtype}: <no answer>"
    # answer is an Answer object; iterate rdata
    for rdata in answer:
        # Many rdata types stringify sensibly; include TTL and to_text where helpful
        try:
            txt = rdata.to_text()
        except Exception:
            txt = str(rdata)
        lines.append(f"  - {txt}")
    return f"{qtype} ({len(answer)}):\n" + "\n".join(lines)

async def run_queries(name: str, qtypes: List[str], servers: List[str], timeout: float):
    resolver = dns.asyncresolver.Resolver()
    if servers:
        resolver.nameservers = servers

    tasks = [query_type(name, q.upper(), resolver, timeout) for q in qtypes]
    results = await asyncio.gather(*tasks)
    return results

def is_ip(s: str):
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        return False

def main():
    p = argparse.ArgumentParser(description="Async terminal DNS lookup tool (dnspython)")
    p.add_argument("name", help="Domain name or IP (for PTR with --ptr)")
    p.add_argument("--types", "-t", default=",".join(DEFAULT_TYPES),
                   help="Comma-separated record types (A,AAAA,MX,NS,TXT,CNAME,SOA,PTR). Default: A,AAAA,MX,NS,TXT,CNAME,SOA")
    p.add_argument("--server", "-s", default="", help="Comma-separated DNS resolver IPs (e.g. 1.1.1.1,8.8.8.8)")
    p.add_argument("--timeout", type=float, default=5.0, help="Per-query timeout seconds (default 5)")
    p.add_argument("--ptr", action="store_true", help="Perform reverse PTR lookup if the input is an IP")
    args = p.parse_args()

    servers = [s.strip() for s in args.server.split(",") if s.strip()]
    qtypes = [t.strip().upper() for t in args.types.split(",") if t.strip()]

    # If user asked for PTR explicitly and provided IP (or gave --ptr), handle reverse
    if args.ptr or (is_ip(args.name) and "PTR" in qtypes):
        # if input is IP, build PTR name
        if not is_ip(args.name):
            print("Error: PTR lookup requires an IP address as the name.", file=sys.stderr)
            sys.exit(2)
        rev = dns.reversename.from_address(args.name).to_text()
        qtypes = ["PTR"]
        target = rev
    else:
        # If the user passed an IP without --ptr, treat it as normal name (likely will fail)
        target = args.name

    # Run asyncio loop
    try:
        results = asyncio.run(run_queries(target, qtypes, servers, args.timeout))
    except KeyboardInterrupt:
        print("\nAborted by user", file=sys.stderr)
        sys.exit(1)

    # Print results
    for qtype, answer, error in results:
        if error:
            print(f"{qtype}: ERROR: {error}")
        else:
            print(format_answer(qtype, answer))

if __name__ == "__main__":
    main()
