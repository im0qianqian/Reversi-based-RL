import socketserver
import ssl
from src.games.reversi.reversi_game import ReversiGame
from src.games.reversi.reversi_player import *
from src.games.reversi.reversi_nnet import NNetWrapper as NNet
from src.config import *


class ReversiWebSSLServer(socketserver.BaseRequestHandler):

    def __send(self, message):
        self.request.sendall(
            ('HTTP/1.1 200 OK\nAccess-Control-Allow-Origin: *\nContent-Type: application/json\n\n' + message).encode(
                encoding='utf-8'))

    def __pre_exec(self, request):
        """预处理请求头"""
        return request.strip('\r\n ').split('\n')[-1]

    def __exec(self, message):
        """处理请求（待填充）"""
        resp = {}
        try:
            requests = json.loads(message)
            resp['status'] = 0
            resp['message'] = "Hello World!"

            mode = requests['mode']  # 请求模式（当前棋盘状态/比赛过程序列）
            data = np.array(json.loads(requests['data'])) * requests['color']  # 棋盘数据

            if mode == 'board':
                action = reversi_ai.play(data)[0]
                resp['response'] = int(action)
            else:
                pass
        except Exception as e:
            resp['status'] = 1
            resp['message'] = "Exec error" + str(e)

        print('client: ', self.client_address)
        print('message: ', message)
        print('response: ', resp)
        print('--------------------')
        return json.dumps(resp)

    def handle(self):
        request = self.request.recv(1024).decode(encoding='utf-8')
        message = self.__pre_exec(request)
        res = self.__exec(message)
        self.__send(res)


if __name__ == "__main__":
    # 初始化 RL player
    game = ReversiGame(8)
    nnet = NNet(game, default_args)
    nnet.nnet.model._make_predict_function()  # 这一句是在使用 keras 时需要在多线程预测之前执行的
    reversi_ai = ReversiRLPlayer(game=game, choice_mode=0, nnet=nnet,
                                 check_point=[default_args.checkpoint_folder, default_args.best_folder_file],
                                 args=default_args)

    # 建立 web 服务器
    http_host = default_args.web_http_host

    # 加载 SSL
    cert_file = default_args.web_ssl_cert_file
    key_file = default_args.web_ssl_key_file
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)

    wsServer = socketserver.ThreadingTCPServer(http_host, ReversiWebSSLServer)
    wsServer.socket = context.wrap_socket(wsServer.socket, server_side=True)

    print('The server is running on port %d' % http_host[1])
    print('The url is http://%s:%d' % http_host)
    wsServer.serve_forever()
