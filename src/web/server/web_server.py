import socket
from src.web.server.exec_request import ReversiExecServer
from src.games.reversi.reversi_game import ReversiGame
from src.games.reversi.reversi_player import *
from src.games.reversi.reversi_nnet import NNetWrapper as NNet
from src.config import *


class ReversiWebServer(object):
    """
    一个简单的 web 服务器，用来解析客户端发送来的请求，创建线程处理它
    """

    def __init__(self, http_host=('localhost', 9420)):
        self.http_host = http_host
        self.game = ReversiGame(8)
        nnet = NNet(self.game, default_args)

        nnet.nnet.model._make_predict_function()  # 这一句是在使用 keras 时需要在多线程预测之前执行的
        self.reversi_ai = ReversiRLPlayer(game=self.game, choice_mode=0, nnet=nnet,
                                          check_point=[default_args.checkpoint_folder, default_args.best_folder_file],
                                          args=default_args)

    def listen(self):
        listen_socket = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM)  # 使用 TCP 连接
        try:
            listen_socket.bind(self.http_host)
            listen_socket.listen()

            print('The server is running on port %d' % self.http_host[1])
            print('The url is http://%s:%d' % self.http_host)

            try:
                while True:
                    client, address = listen_socket.accept()
                    ReversiExecServer(client, address, self.reversi_ai).start()
            except Exception as e:
                print(e)
        except Exception as e:
            listen_socket.close()
            print(e)


if __name__ == '__main__':
    server = ReversiWebServer(default_args.web_http_host)
    server.listen()
