import threading
import json
import numpy as np


class ReversiExecServer(threading.Thread):
    """
    执行从客户端发送来的请求
    """

    def __init__(self, client, address, reversi_ai):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.reversi_ai = reversi_ai

    def __send(self, message):
        self.client.sendall(
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
            self.reversi_ai.player_id = requests['color']  # AI 颜色（黑色 1，白色 -1）
            data = np.array(json.loads(requests['data']))  # 棋盘数据

            if mode == 'board':
                action = self.reversi_ai.play(data)
                resp['response'] = int(action)
            else:
                pass
        except Exception as e:
            resp['status'] = 1
            resp['message'] = "Exec error" + str(e)

        print('message: ', message)
        print('response: ', resp)
        print('--------------------')
        return json.dumps(resp)

    def run(self):
        request = self.client.recv(1024).decode(encoding='utf-8')
        message = self.__pre_exec(request)
        res = self.__exec(message)
        print('res', res)
        self.__send(res)
        self.client.close()
