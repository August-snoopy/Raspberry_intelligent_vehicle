from socket import *

sock = socket(AF_INET, SOCK_DGRAM)
while True:
    data = input()
    sock.sendto(data.encode(), ('192.168.43.150', 8005))
    res, address = sock.recvfrom(1024)
    print(res.decode())