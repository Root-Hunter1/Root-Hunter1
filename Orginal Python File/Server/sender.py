import socket, time

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
start = time.time()
N = 100000
for i in range(N):
    s.sendto(b"test packet %d" % i, ("127.0.0.1", 9999))
elapsed = time.time() - start
print(f"{N} packets in {elapsed:.2f}s = {N/elapsed:.0f} pkt/s")
