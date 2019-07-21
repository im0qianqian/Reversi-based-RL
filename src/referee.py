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

    def play_games(self, num, verbose=False, exit_threshold=(float('inf'), float('inf'))):
        """
        exit_threshold 代表是否提前结束的阈值，其实不想加这个的，因为感觉对面向对象设计有点***，但为了快速的训练，还是加上吧
            其中两个参数分别是 player1_won 与 player2_won 超过它时退出
        """
        player1_won = 0
        player2_won = 0
        draws = 0
        start_time = time.time()
        for _ in range(num):
            result = self.play_game(verbose=verbose)
            if result == self.game.WinnerState.DRAW:
                draws += 1
            elif result == self.game.WinnerState.PLAYER1_WIN:
                player1_won += 1
            else:
                player2_won += 1
            print(
                'arena compare player1 --> player2, eps: {} / {}, player1_won: {}, player2_won: {}, draws: {}, time: {}'.format(
                    _ + 1, num, player1_won, player2_won, draws, time.time() - start_time))
            start_time = time.time()
            if player1_won > exit_threshold[0] or player2_won > exit_threshold[1]:
                print('exit_threshold trigger, exit now...')
                return player1_won, player2_won, draws

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
            print(
                'arena compare player2 --> player1, eps: {} / {}, player1_won: {}, player2_won: {}, draws: {},time: {}'.format(
                    _ + 1, num, player1_won, player2_won, draws, time.time() - start_time))
            start_time = time.time()
            if player1_won > exit_threshold[0] or player2_won > exit_threshold[1]:
                print('exit_threshold trigger, exit now...')
                return player1_won, player2_won, draws

        return player1_won, player2_won, draws


if __name__ == "__main__":
    game = ReversiGame(8)

    randomAI = ReversiRandomPlayer(game)
    greedyAI1 = ReversiGreedyPlayer(game, greedy_mode=0)
    greedyAI2 = ReversiGreedyPlayer(game, greedy_mode=1)
    humanAI = ReversiHumanPlayer(game)
    botzoneAI = ReversiBotzonePlayer(game)
    # 加载旧模型玩家（旧的 best_folder_file）
    n_player = ReversiRLPlayer(game=game, choice_mode=0, nnet=None,
                               check_point=[default_args.checkpoint_folder,
                                            default_args.best_folder_file],
                               args=default_args)
    # p_player = ReversiRLPlayer(game=game, choice_mode=0, nnet=None,
    #                            check_point=[default_args.checkpoint_folder,
    #                                         default_args.best_folder_file],
    #                            args=default_args)

    referee = Referee(n_player, n_player, game)

    print('start ...')
    time0 = time.time()
    for i in range(1):
        print(referee.play_game(verbose=False))
    time1 = time.time()
    print('time: ', time1 - time0)

    # game = ReversiGame(8)
    #
    # path = r'/content/gdrive/My Drive/Reversi-based-RL/data'
    #
    # lst = [0, 15, 24, 32, 48, 75, 89, 95, 102, 118]
    # for i in range(10):
    #     for j in range(i + 1, 10):
    #         print(lst[i], 'vs', lst[j])
    #         p1 = ReversiRLPlayer(game=game, choice_mode=0, nnet=None,
    #                              check_point=[path, 'checkpoint_{}_update.h5'.format(lst[i])],
    #                              args=default_args)
    #         p2 = ReversiRLPlayer(game=game, choice_mode=0, nnet=None,
    #                              check_point=[path, 'checkpoint_{}_update.h5'.format(lst[j])],
    #                              args=default_args)
    #         n_wins, p_wins, draws = Referee(p1, p2, game).play_games(10, verbose=False)
    #         print('{} vs {} wins : {} / {}, draws : {}'.format(i, j, n_wins, p_wins, draws))

    # def getFileMD5(filepath):
    #     import hashlib
    #     f = open(filepath, 'rb')
    #     md5obj = hashlib.md5()
    #     md5obj.update(f.read())
    #     hash = md5obj.hexdigest()
    #     f.close()
    #     return str(hash).upper()

    # for i in range(20):
    #     print(i, getFileMD5(path + '/best({}).pth.tar'.format(i)))
