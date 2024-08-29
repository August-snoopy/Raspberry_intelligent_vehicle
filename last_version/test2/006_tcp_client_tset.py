# tcp客户端
from socket import *

# 创建套接字
sock = socket()

try:
    # 连接服务器
    sock.connect(('192.168.43.150', 8000))
    # 收发消息
    while True:
        res = sock.recv(1024)
        if not res:
            print("Server disconnected.")
            break
        print(res.decode())
        if res.decode() == '请发送一条命令。':
            print("Please enter your command:")
            data = input()
            if data == "q":
                print("Exiting...")
                break
            sock.send(data.encode())
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    sock.close()