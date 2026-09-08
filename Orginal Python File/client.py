#!/usr/bin/env python3
"""
Terminal HTTP Chat client.

Usage:
  pip install requests
  python3 client.py --server http://localhost:8000 --user alice

Behavior:
 - Starts a background poller to GET /messages?since=<id>
 - Main thread reads user input and POSTs to /send
"""
import argparse
import requests
import threading
import time
import sys
import queue

def poller(server, last_id_ref, stop_event, out_q, interval):
    url = server.rstrip('/') + '/messages'
    while not stop_event.is_set():
        try:
            resp = requests.get(url, params={'since': last_id_ref[0]}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get('messages', []):
                    out_q.put(m)
                    last_id_ref[0] = max(last_id_ref[0], m['id'])
        except Exception as e:
            # Put an error message to out queue occasionally
            out_q.put({"user": "system", "text": f"Poll error: {e}", "ts": time.time(), "id": 0})
        # wait with early exit possibility
        for _ in range(int(interval * 10)):
            if stop_event.is_set():
                break
            time.sleep(0.1)

def print_loop(out_q, stop_event):
    while not stop_event.is_set():
        try:
            m = out_q.get(timeout=0.5)
        except queue.Empty:
            continue
        try:
            ts = time.strftime('%H:%M:%S', time.localtime(m.get('ts', time.time())))
            user = m.get('user', 'unknown')
            text = m.get('text', '')
            print(f"[{ts}] {user}: {text}")
        except Exception:
            # defensive
            print(f"[{time.strftime('%H:%M:%S')}] (bad message) {m}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--server', default='http://127.0.0.1:8000', help='Server base URL')
    p.add_argument('--user', default='guest', help='Your user name')
    p.add_argument('--interval', type=float, default=1.0, help='Polling interval in seconds')
    args = p.parse_args()

    last_id = [0]
    stop_event = threading.Event()
    out_q = queue.Queue()

    poll_thread = threading.Thread(target=poller, args=(args.server, last_id, stop_event, out_q, args.interval), daemon=True)
    printer_thread = threading.Thread(target=print_loop, args=(out_q, stop_event), daemon=True)

    poll_thread.start()
    printer_thread.start()

    print("Type messages and press Enter. Ctrl-C to quit.")
    try:
        while True:
            try:
                line = input()
            except EOFError:
                break
            text = line.strip()
            if not text:
                continue
            payload = {'user': args.user, 'text': text}
            try:
                resp = requests.post(args.server.rstrip('/') + '/send', json=payload, timeout=5)
                if resp.status_code not in (200, 201):
                    print("Send error:", resp.status_code, resp.text)
            except Exception as e:
                print("Send failed:", e)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nExiting...")
        stop_event.set()
        poll_thread.join(timeout=2)
        printer_thread.join(timeout=1)

if __name__ == '__main__':
    main()
