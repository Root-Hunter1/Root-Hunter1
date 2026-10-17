vlen up:
python send.py --procs 3 --socks 4 --vlen 256


python send.py --procs 2 --socks 8
python send.py --procs 3 --socks 8
python send.py --procs 4 --socks 4

python package size short:
python send.py --size 32

line chages 19number: libc = ctypes.CDLL("libc.so.6", use_errno=True)
only mobile version: libc = ctypes.CDLL("libc.so", use_errno=True)
