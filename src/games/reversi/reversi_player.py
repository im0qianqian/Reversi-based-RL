import urllib
import time
import urllib.request
import json

from src.games.player import Player
import numpy as np


class ReversiRandomPlayer(Player):
    """
    随机AI
    """

    def play(self, board=None):
        legal_moves_np = self.game.get_legal_moves(self.player_id,
                                                   board).reshape(-1)  # 获取可行动的位置
        legal_moves = []
        for i in range(self.game.n ** 2):
            if legal_moves_np[i]:
                legal_moves.append(i)
        print('legal moves: ', legal_moves)
        if len(legal_moves) == 0:  # 无子可下
            return -1
        return legal_moves[np.random.randint(len(legal_moves))]


class ReversiHumanPlayer(Player):
    """
    人类AI，即手动操作
    """

    def play(self, board=None):
        legal_moves_np = self.game.get_legal_moves(self.player_id,
                                                   board).reshape(-1)  # 获取可行动的位置
        legal_moves = []
        for i in range(self.game.n ** 2):
            if legal_moves_np[i]:
                legal_moves.append((i // self.game.n, i % self.game.n))
        print(legal_moves)
        while True:
            try:
                x, y = map(int, input().split())
                if len(legal_moves) == 0 and x == -1:
                    return -1
                else:
                    action = x * self.game.n + y
                    if legal_moves_np[action]:
                        return action
                    else:
                        print("error!")
            except Exception as e:
                print(e)


class ReversiBotzonePlayer(Player):
    """
    Connects to Botzone
    """

    def __init__(self, game, player_id, description=""):
        super().__init__(game, player_id, description)
        self.matches = {}
        self.referee = None
        pass

    class Match:
        has_request = False
        has_response = False
        current_request = None
        current_response = None
        matchid = None

        def new_request(self, request):
            self.has_request = True
            self.has_response = False
            self.current_request = request

    # TODO：定义一种特化的对局数据类，比如存储棋盘状态等
    class SomeKindOfMatch(Match):
        def __init__(self, matchid, first_request):
            self.has_request = True
            self.current_request = first_request
            self.matchid = matchid

    # 从 Botzone 上拉取新的对局请求
    def fetch(self, matchClass):
        req = urllib.request.Request(
            "https://www.botzone.org.cn/api/576dea8e28a77f3c04a22ec3/qianqian/localai"
        )
        for matchid, m in self.matches.items():
            if m.has_response and m.has_request and m.current_response:
                print('> Response for match [%s]: %s' % (matchid,
                                                         m.current_response))
                m.has_request = False
                req.add_header("X-Match-" + matchid, m.current_response)
        while True:
            try:
                res = urllib.request.urlopen(req, timeout=None)
                botzone_input = res.read().decode()
                lines = botzone_input.split('\n')
                request_count, result_count = map(int, lines[0].split(' '))
                for i in range(0, request_count):
                    # 新的 Request
                    matchid = lines[i * 2 + 1]
                    request = lines[i * 2 + 2]
                    if matchid in self.matches:
                        print('> Request for match [%s]: %s' % (matchid, request))
                        self.matches[matchid].new_request(request)
                    else:
                        print('New match [%s] with first request: %s' % (matchid,
                                                                         request))
                        self.matches[matchid] = matchClass(matchid, request)
                for i in range(0, result_count):
                    # 结束的对局结果
                    matchid, slot, player_count, *scores = lines[
                        request_count * 2 + 1 + i].split(' ')
                    if player_count == "0":
                        print("Match [%s] aborted:\n> I'm player %s" % (matchid,
                                                                        slot))
                    else:
                        print(
                            "Match [%s] finished:\n> I'm player %s, and the scores are %s"
                            % (matchid, slot, scores))
                    self.matches.pop(matchid)
            except (urllib.error.URLError, urllib.error.HTTPError):
                # 此时可能是长时间没有新的 request 导致连接超时，再试即可
                print(
                    "Error reading from Botzone or timeout, retrying 2 seconds later..."
                )
                time.sleep(2)
                continue
            break

    def play(self, board=None):
        self.fetch(self.SomeKindOfMatch)
        resp = dict()
        last_action = self.referee.get_last_action()
        for mid, m in self.matches.items():
            if last_action is None:  # 第一次的时候
                break
            if last_action >= self.game.n ** 2 or last_action < 0:
                resp['x'] = -1
                resp['y'] = -1
            else:
                resp['x'] = last_action % self.game.n
                resp['y'] = last_action // self.game.n

            m.current_response = json.dumps(resp)
            # 将自己的动作存入 m.current_response，同样进行一步模拟
            m.has_response = True

        self.fetch(self.SomeKindOfMatch)

        action = -1
        for mid, m in self.matches.items():
            # 使用 m.current_request 模拟一步对局状态，然后产生动作
            botzone_action = json.loads(m.current_request)
            action = int(botzone_action['y']) * self.game.n + int(botzone_action['x'])
        return action if 0 <= action < self.game.n ** 2 else -1


if __name__ == "__main__":
    pass
