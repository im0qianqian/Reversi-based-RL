import threading


class ReversiExecServer(threading.Thread):
    """
    执行从客户端发送来的请求
    """

    def __init__(self, client, address):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address

    def __send(self, message):
        self.client.sendall(
            ('HTTP/1.1 200 OK\nContent-Type: text/html\n\n' + message).encode(
                encoding='utf-8'))

    def __pre_exec(self, request):
        """预处理请求头"""
        return request.strip('\r\n ').split('\n')[-1]

    def __exec(self, message):
        """处理请求（待填充）"""
        return message

    def run(self):
        request = self.client.recv(1024).decode(encoding='utf-8')
        message = self.__pre_exec(request)
        res = self.__exec(message)
        self.__send(res)
        self.client.close()
