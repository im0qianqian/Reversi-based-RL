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
        self.__pi_list = []  # 棋盘序列预测概率值
        self.__action_list = []  # 所有执行过的动作，嗯~ 用于 botzone 交互时得知对方的走棋状态（其实一步就可以了不需要一个列表QAQ）
        pass

    def get_last_action(self):
        """获取最后一次执行的动作，若当前无动作返回 None"""
        if len(self.__action_list) == 0:
            return None
        return self.__action_list[-1]

    def get_pi_list(self):
        """获取所有预测概率序列"""
        return self.__pi_list

    def get_baord_list(self):
        """获取所有的棋盘序列"""
        return self.__board

    def init(self):
        self.__board.clear()
        self.__pi_list.clear()
        self.__action_list.clear()

    def play_game(self, verbose=False):
        """开始游戏"""
        self.init()

        current_player = 1
        current_board = self.game.init()

        # 记录第一步
        self.__board.append(current_board)

        self.player1.init(referee=self)  # 先初始化，必须要做
        self.player2.init(referee=self)

        player = [self.player2, None, self.player1]
        step = 1  # 行走的步数
        while self.game.get_winner(current_board) == self.game.WinnerState.GAME_RUNNING:
            action, *prob = player[current_player + 1].play(
                self.game.get_relative_state(current_player, current_board))  # 返回对 current_board 的走法以及预测行走概率
            if verbose:
                self.game.display(current_board)
                print("step {} {} --> {}".format(step, player[current_player + 1].description,
                                                 (-1, -1) if action == -1 else (
                                                     action // self.game.n, action % self.game.n)))
            self.__action_list.append(action)
            self.__pi_list.append([] if len(prob) == 0 else prob[0])
            if action != -1:
                # action == -1 or action == self.n ** 2 代表无路可走的情况
                legal_moves = self.game.get_legal_moves(current_player, current_board)
                assert legal_moves[action] == 1
            current_board, current_player = self.game.get_next_state(current_player, action, current_board)
            # 记录历史棋盘，一方面可以用来训练神经网络
            self.__board.append(current_board)
            step += 1
        # 对局结束后双方 AI 各走一步，主要是使某些延迟类 AI 知道此时游戏已经结束了（但还是存在 bug）
        player[current_player + 1].play(current_board)
        player[-current_player + 1].play(current_board)

        if verbose:
            print('---------------------------')
            self.game.display(current_board)
            print(
                "黑棋胜利！" if self.game.get_winner(
                    current_board) == self.game.WinnerState.PLAYER1_WIN else "白棋胜利！" if self.game.get_winner(
                    current_board) == self.game.WinnerState.PLAYER2_WIN else "平局！")
        return self.game.get_winner(current_board)

    def play_games(self, num, verbose=False):
        player1_won = 0
        player2_won = 0
        draws = 0
        for _ in range(num):
            result = self.play_game(verbose=verbose)
            if result == self.game.WinnerState.DRAW:
                draws += 1
            elif result == self.game.WinnerState.PLAYER1_WIN:
                player1_won += 1
            else:
                player2_won += 1
            print('arena compare player1 --> player2, eps: {} / {}, player1_won: {}, player2_won: {}, draws: {}'.format(
                _ + 1, num, player1_won, player2_won, draws))

        # 以下反转两个玩家再进行 num 次
        self.player1, self.player2 = self.player2, self.player1
        for _ in range(num):
            result = self.play_game(verbose=verbose)
            if result == self.game.WinnerState.DRAW:
                draws += 1
            elif result == self.game.WinnerState.PLAYER2_WIN:
                player1_won += 1
            else:
                player2_won += 1
            print('arena compare player2 --> player1, eps: {} / {}, player1_won: {}, player2_won: {}, draws: {}'.format(
                _ + 1, num, player1_won, player2_won, draws))

        return player1_won, player2_won, draws


if __name__ == "__main__":
    game = ReversiGame(8)

    randomAI = ReversiRandomPlayer(game)
    greedyAI1 = ReversiGreedyPlayer(game, greedy_mode=0)
    greedyAI2 = ReversiGreedyPlayer(game, greedy_mode=1)
    humanAI = ReversiHumanPlayer(game)
    botzoneAI = ReversiBotzonePlayer(game)
    # n1p = ReversiRLPlayer(game=game, choice_mode=1, check_point=['../data', '8x8_100checkpoints_best.pth.tar'])
    n2p = ReversiRLPlayer(game=game, choice_mode=1,
                          check_point=[default_args.checkpoint_folder, default_args.best_folder_file])

    referee = Referee(n2p, n2p, game)

    print('start ...')
    time0 = time.time()
    for i in range(1):
        print(referee.play_game(verbose=False))
    time1 = time.time()
    print('time: ', time1 - time0)
