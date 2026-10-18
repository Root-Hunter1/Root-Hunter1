./sender2 127.0.0.1 9999 2 4 0 0 0
./sender2 127.0.0.1 9999 4 4 0 0 0                                            ./sender2 127.0.0.1 9999 2 4 0 0 0
./sender2 127.0.0.1 9999 4 4 0 0 0

গ) থ্রেড সংখ্যা বদলে দেখুন:

./sender2 127.0.0.1 9999 2 4 0 0 0
./sender2 127.0.0.1 9999 4 4 0 0 0

ঘ) ফোন ঠান্ডা করে ছোট টেস্ট: ফোনকে বিশ্রাম দিয়ে ১০-২০ সেকেন্ডের ছোট রান দিন:

./sender2 127.0.0.1 9999 3 4 200000 200000 1000000 3


compaline:

clang -O2 -pthread -o sender2 sender2.c

# Terminal 1: Server (initially without DB)
# টার্মিনাল ১: সার্ভার (আগে DB ছাড়া)
python udp_pg.py --procs 3

# Terminal 2: In stages, from 200,000 to 2 million/s
# টার্মিনাল ২: ২ লাখ থেকে ২০ লাখ/s পর্যন্ত ধাপে ধাপে
./sender2 127.0.0.1 9999 3 4 200000 200000 2000000 5

# Maximum speed only (excluding ramps)
# শুধু সর্বোচ্চ গতি (র‍্যাম্প ছাড়া)
./sender2 127.0.0.1 9999 3 4 0 0 0

#To see the maximum speed (without a ramp):
#সর্বোচ্চ গতি দেখতে (র‍্যাম্প ছাড়া):

./sender2 127.0.0.1 9999 3 4 0 0 0
