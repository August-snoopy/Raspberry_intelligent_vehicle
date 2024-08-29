from  socket import *
sock=socket(AF_INET,SOCK_DGRAM)
while True:

    data=input('请使用小键盘输入指令')
    sock.sendto(data.encode(),('192.168.137.106',8300))
    res,address=sock.recvfrom(1024)
    print(res.decode())