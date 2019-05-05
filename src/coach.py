from src.referee import Referee
from src.games.reversi.reversi_game import ReversiGame as Game
from src.games.reversi.reversi_player import *
from src.config import *


class Coach(object):
    """
    reinforcement learning self-play
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        pass

    def execute_episode(self, player1, player2):
        train_examples = []

        # 游戏初始化棋盘
        self.game.init()
        # 创建裁判类
        referee = Referee(player1=player1, player2=player2, game=self.game)
        # 游戏开始
        result = referee.play_game(verbose=False)
        # e 只是一个控制当前是黑棋还是白棋的变量
        e = 1
        # v 表示哪个玩家胜利了
        v = 0 if result == self.game.WinnerState.DRAW else 1 if result == self.game.WinnerState.PLAYER1_WIN else -1

        board_list = referee.get_baord_list()[:-1]  # 去除最后一个的原因：1. 最后一个棋盘是终止态 2. 与 pi 一一对应
        pi_list = referee.get_pi_list()  # 这里的 pi 全部是对 CanonicalForm 而言的，即对白棋来说 board * -1 对应这个 pi
        for i in range(len(board_list)):
            train_examples.append((e * board_list[i], pi_list[i], v))
            e = -e
            v = -v
        return train_examples

    def start_learn(self):
        """学习学习"""
        pass


if __name__ == '__main__':
    g = Game(8)
    coach = Coach(g, None, default_nnet_args)

    n1p = ReversiRLPlayer(game=g, choice_mode=1, check_point=['../data', '8x8_100checkpoints_best.pth.tar'])
    n2p = ReversiRLPlayer(game=g, choice_mode=1, check_point=['../data', '8x8_100checkpoints_best.pth.tar'])

    examples = coach.execute_episode(n1p, n2p)
    pass
