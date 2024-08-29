# 树莓派接受指令和处理指令的服务器
# 1. 创建UDP套接字
from socket import *

# 创建UDP套接字
sock = socket(AF_INET, SOCK_DGRAM)
# 绑定地址
sock.bind(('192.168.43.150', 8000))
# 循环收发数据
while True:
    # 接受数据
    data, address = sock.recvfrom(1024)
    # 打印数据
    print(data.decode())
    if data.decode() == 'w':
        print('前进')
    elif data.decode() == 's':
        print('后退')
    elif data.decode() == 'a':
        print('左移')
    elif data.decode() == 'd':
        print('右移')
    # 发送数据
    sock.sendto('执行成功'.encode(), address)