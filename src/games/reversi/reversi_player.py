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

    def play(self, board):
        legal_moves_np = self.game.get_legal_moves(self.player_id,
                                                   board)  # 获取可行动的位置
        legal_moves = []
        for i in range(self.game.n ** 2):
            if legal_moves_np[i]:
                legal_moves.append(i)
        print('legal moves: ', list(map(lambda x: (x // self.game.n, x % self.game.n), legal_moves)))
        if len(legal_moves) == 0:  # 无子可下
            return -1
        return legal_moves[np.random.randint(len(legal_moves))]


class ReversiGreedyPlayer(Player):
    """
    基于贪心的 AI
    """

    def __init__(self, game, description="", greedy_mode=0):
        """
        greedy mode
        =0 可贪心使得当前转换棋子数量最大
        =1 可贪心使得对方行动力最小（哭了哭了，太假了）
        """
        super().__init__(game, description)
        # 贪心策略
        self.greedy_mode = greedy_mode

    def play(self, board):
        legal_moves_np = self.game.get_legal_moves(self.player_id,
                                                   board)  # 获取可行动的位置
        legal_moves = []
        for i in range(self.game.n ** 2):
            if legal_moves_np[i]:
                legal_moves.append(i)
        if len(legal_moves) == 0:  # 无子可下
            return -1

        if self.greedy_mode == 0:
            # 贪心使得当前转换棋子数量最大
            action = -1
            max_greedy = -self.game.n ** 2
            for i in legal_moves:
                board_tmp, _ = self.game.get_next_state(self.player_id, i, board)
                sum_tmp = np.sum(board_tmp) * self.player_id
                # print((i // self.game.n, i % self.game.n), ' greedy: ', sum_tmp)
                if max_greedy < sum_tmp:
                    max_greedy = sum_tmp
                    action = i
            # print((action // self.game.n, action % self.game.n), ' max greedy: ', max_greedy)
            return action
        else:
            # 贪心使得对方行动力最小
            action = -1
            max_greedy = self.game.n ** 2
            for i in legal_moves:
                board_tmp, _ = self.game.get_next_state(self.player_id, i, board)
                # 对方可移动位置
                legal_moves_tmp = self.game.get_legal_moves(_, board_tmp)
                sum_tmp = np.sum(legal_moves_tmp[:-1])
                # print((i // self.game.n, i % self.game.n), ' greedy: ', sum_tmp)
                if max_greedy > sum_tmp:
                    max_greedy = sum_tmp
                    action = i
            # print((action // self.game.n, action % self.game.n), ' max greedy: ', max_greedy)
            return action


class ReversiHumanPlayer(Player):
    """
    人类AI，即手动操作
    """

    def play(self, board):
        legal_moves_np = self.game.get_legal_moves(self.player_id,
                                                   board)  # 获取可行动的位置
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

    def __init__(self, game, description=""):
        super().__init__(game, description)
        self.matches = {}
        self.is_finished = False

    def init(self, player_id, referee=None):
        super().init(player_id, referee)
        self.matches = {}
        self.is_finished = False
        self.fetch(self.SomeKindOfMatch)

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
                        self.is_finished = True
                    self.matches.pop(matchid)
            except (urllib.error.URLError, urllib.error.HTTPError):
                # 此时可能是长时间没有新的 request 导致连接超时，再试即可
                print(
                    "Error reading from Botzone or timeout, retrying 2 seconds later..."
                )
                time.sleep(2)
                continue
            break
        return self.is_finished

    def play(self, board):
        resp = dict()
        last_action = self.referee.get_last_action()
        for mid, m in self.matches.items():
            if last_action is None:  # 第一次的时候
                break
            if last_action >= self.game.n ** 2 or last_action < 0:
                resp['x'] = -1
                resp['y'] = -1
            else:
                resp['x'] = int(last_action % self.game.n)
                resp['y'] = int(last_action // self.game.n)

            m.current_response = json.dumps(resp)
            # 将自己的动作存入 m.current_response，同样进行一步模拟
            m.has_response = True

        if not self.is_finished and self.fetch(self.SomeKindOfMatch):
            """
            如果对局已经结束，发生这种情况一般 current_request 没有接收到的下一步，因此我们得自行走最后一步
            容易证明，如果当前可走，则这一步走完以后游戏必定结束
              1. 假设我有多于 1 的行动力，且对局已经结束则说明对方无法在该步后做出行动，然而再下一步我依然可以行动，此假设不成立
              2. 假设我只有 1 的行动力，同上对方无法行动，则该步结束后游戏结束，假设成立
              3. 假设我无法行动，该步并不会做出任何动作，游戏结束，假设成立
            """
            legal_moves_np = self.game.get_legal_moves(self.player_id,
                                                       board)  # 获取可行动的位置
            for i in range(self.game.n ** 2):  # 找到可行动的位置
                if legal_moves_np[i]:
                    print("本地最后一次弥补：", (i // self.game.n, i % self.game.n))
                    return i

        action = -1

        for mid, m in self.matches.items():
            # 使用 m.current_request 模拟一步对局状态，然后产生动作
            botzone_action = json.loads(m.current_request)
            action = int(botzone_action['y']) * self.game.n + int(botzone_action['x'])

        # self.fetch(self.SomeKindOfMatch)
        return action if 0 <= action < self.game.n ** 2 else -1


class ReversiRLPlayer(Player):
    """
    基于强化学习的 AI（正在制作中）
    """

    def __init__(self, game, check_point=None):
        super().__init__(game)

        from src.games.reversi.reversi_nnet import NNetWrapper as NNet
        import os
        self.n1 = NNet(self.game)

        # 临时操作
        if check_point is None:
            self.n1.load_checkpoint(os.path.abspath('') + '/model',
                                    '8x8_100checkpoints_best.pth.tar')
        else:
            self.n1.load_checkpoint(check_point[0], check_point[1])

    def init(self, player_id, referee=None):
        super().init(player_id, referee)

    def play(self, board):
        super().play(board)
        from src.lib.mcts import MCTS

        mcts1 = MCTS(self.game, self.n1)

        counts = mcts1.get_action_probility(board * self.player_id, temp=1)
        # print(counts)
        # print(np.argmax(counts))
        # input()
        return np.argmax(counts)


if __name__ == "__main__":
    pass
