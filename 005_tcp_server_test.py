# tcp服务器
from socket import *
import time
from multiprocessing import Process


class send_recv_class(Process):
    def __init__(self, conn):
        self.conn = conn
        super(send_recv_class, self).__init__()
    def run(self) -> None:
        while True:
            self.conn.send('你好客户端'.encode())
            time.sleep(2)

if __name__ == '__main__':
    sock = socket() # 默认参数为ipv4 和套接字类型
    # bind绑定地址
    sock.bind(('0.0.0.0', 8888))
    # 监听队列
    sock.listen(5)
    # 等待连接
    while True:
        print('等待客户端连接')
        conn, addr = sock.accept()
        # 连接成功后启动一个子任务来处理当前的客户端
        print('新连接的客户端地址为', addr)
        p = send_recv_class(conn)
        p.start()
    # 退出
