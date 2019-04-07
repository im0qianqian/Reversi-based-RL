import socket
from .exec_request import ReversiExecServer


class ReversiWebServer(object):
    """
    一个简单的 web 服务器，用来解析客户端发送来的请求，创建线程处理它
    """

    def __init__(self, http_host=('localhost', 9420)):
        self.http_host = http_host

    def listen(self):
        try:
            listen_socket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)  # 使用 TCP 连接
            listen_socket.bind(self.http_host)
            listen_socket.listen()

            print('The server is running on port %d' % self.http_host[1])
            print('The url is http://%s:%d' % self.http_host)

            try:
                while True:
                    client, address = listen_socket.accept()
                    ReversiExecServer(client, address).start()
            except Exception as e:
                print(e)
        except Exception as e:
            listen_socket.close()
            print(e)