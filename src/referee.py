from src.games.reversi.reversi_player import *
from src.games.reversi.reversi_game import ReversiGame


class Referee(object):
    """
    这是一个裁判类，指挥游戏的正常运行
    """

    def __init__(self, player1, player2, game):
        self.player1 = player1  # player1 是先手
        self.player2 = player2  # player2 是后手
        self.game = game  # 当前游戏
        self.__board = []  # 棋盘所有过程，可用于悔棋
        self.__action_list = []  # 所有执行过的动作，嗯~ 用于 botzone 交互时得知对方的走棋状态（其实一步就可以了不需要一个列表QAQ）
        pass

    def get_last_action(self):
        """获取最后一次执行的动作，若当前无动作返回 None"""
        if len(self.__action_list) == 0:
            return None
        return self.__action_list[-1]

    def resume(self):
        """悔棋一步"""
        if len(self.__board):
            self.game.init(self.__board[-1])

    def start_game(self):
        """开始游戏"""
        current_player = 1
        current_board = self.game.get_current_state()

        # 记录第一步
        self.__board.append(current_board)

        self.player1.init(current_player, self)  # 先初始化，必须要做
        self.player2.init(-current_player, self)

        player = [self.player2, None, self.player1]
        step = 1  # 行走的步数
        while self.game.get_winner(current_board) == self.game.WinnerState.GAME_RUNNING:
            self.game.display(current_board)
            action = player[current_player + 1].play(current_board)
            print("step {} {} --> {}".format(step, player[current_player + 1].description,
                                             (-1, -1) if action == -1 else (
                                                 action // self.game.n, action % self.game.n)))
            self.__action_list.append(action)
            if action != -1:
                # action == -1 or action == self.n ** 2 代表无路可走的情况
                legal_moves = self.game.get_legal_moves(current_player, current_board)
                assert legal_moves[action] == 1
            current_board, current_player = self.game.get_next_state(current_player, action, current_board)
            self.__board.append(current_board)
            step += 1
        print('---------------------------')
        # 对局结束后双方 AI 各走一步，主要是使某些延迟类 AI 知道此时游戏已经结束了（但还是存在 bug）
        player[current_player + 1].play(current_board)
        player[-current_player + 1].play(current_board)
        self.game.display(current_board)
        print(
            "黑棋胜利！" if game.get_winner(
                current_board) == self.game.WinnerState.PLAYER1_WIN else "白棋胜利！" if game.get_winner(
                current_board) == self.game.WinnerState.PLAYER2_WIN else "平局！")


if __name__ == "__main__":
    game = ReversiGame(8)

    randomAI1 = ReversiRandomPlayer(game)
    randomAI2 = ReversiRandomPlayer(game)
    greedyAI1 = ReversiGreedyPlayer(game, greedy_mode=0)
    greedyAI2 = ReversiGreedyPlayer(game, greedy_mode=1)
    humanAI = ReversiHumanPlayer(game)
    botzoneAI = ReversiBotzonePlayer(game)
    n1p = ReversiRLPlayer(game, ['../data', '8x8_100checkpoints_best.pth.tar'])
    n2p = ReversiRLPlayer(game, ['../data', '8x8_100checkpoints_best.pth.tar'])

    referee = Referee(n1p, n2p, game)

    time0 = time.time()
    for i in range(1):
        referee.start_game()
    time1 = time.time()
    print('time: ', time1 - time0)
    pass
