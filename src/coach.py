from src.referee import Referee
from src.games.reversi.reversi_game import ReversiGame as Game
from src.games.reversi.reversi_player import *
from src.config import *
from src.lib.utils import *
from collections import deque
from src.games.reversi.reversi_nnet import NNetWrapper as NNet


class Coach(object):
    """
    reinforcement learning self-play
    """

    def __init__(self, game, args):
        self.game = game
        self.args = args
        # self.nnet = NNet(self.game, self.args)
        # self.pnet = NNet(self.game, self.args)
        # self.n_player = ReversiRLPlayer(self.game, choice_mode=0, nnet=self.nnet, args=self.args)
        # self.p_player = ReversiRLPlayer(self.game, choice_mode=0, nnet=self.pnet, args=self.args)
        self.train_examples_history = deque(maxlen=self.args.num_train_examples_history)

    def execute_episode(self, game, player1, player2):
        train_examples = []

        # 游戏初始化棋盘
        game.init()
        # 创建裁判类
        referee = Referee(player1=player1, player2=player2, game=game)
        # 游戏开始
        result = referee.play_game(verbose=True)
        # e 只是一个控制当前是黑棋还是白棋的变量
        e = 1
        # v 表示哪个玩家胜利了
        v = 0 if result == game.WinnerState.DRAW else 1 if result == game.WinnerState.PLAYER1_WIN else -1

        board_list = referee.get_baord_list()[:-1]  # 去除最后一个的原因：1. 最后一个棋盘是终止态 2. 与 pi 一一对应
        pi_list = referee.get_pi_list()  # 这里的 pi 全部是对 CanonicalForm 而言的，即对白棋来说 board * -1 对应这个 pi
        for i in range(len(board_list)):
            symmetries = game.get_symmetries(e * board_list[i], pi_list[i])
            for board, pi in symmetries:  # 这里是 board 的旋转以及对称，因为这些操作不会影响局面形式
                train_examples.append((board, pi, v))
            e = -e
            v = -v
        return train_examples

    def async_execute_episode(self, game, args):
        # set_gpu_memory_grow()
        n_player = ReversiRLPlayer(game, choice_mode=0, check_point=args.load_folder_file, args=args)
        p_player = ReversiRLPlayer(game, choice_mode=0, check_point=args.load_folder_file, args=args)
        # g = game.__class__(8)
        # n_player = ReversiRandomPlayer(g)
        # p_player = ReversiRandomPlayer(g)
        # return 'Hello'
        return self.execute_episode(g, n_player, p_player)

    def start_learn(self):
        """学习学习"""
        for i in range(self.args.num_iteration):  # 迭代
            print("----------------- 第 {} 次迭代 ----------------".format(i))

            train_examples_i = deque([], maxlen=self.args.num_iteration_train_examples)
            for eps in range(self.args.num_episode):
                print('execute episode {} / {}'.format(eps + 1, self.args.num_episode))
                train_examples_i += self.execute_episode(self.n_player, self.p_player)
            self.train_examples_history.append(train_examples_i)

            self.nnet.save_checkpoint(folder=self.args.checkpoint_folder, filename='tmp.pth.tar')
            self.pnet.load_checkpoint(folder=self.args.checkpoint_folder, filename='tmp.pth.tar')

            # 整理之前所有 train_examples_history 进行训练
            train_examples = []
            for e in self.train_examples_history:
                train_examples.extend(e)
            self.nnet.train(train_examples)
            print('------- iteration {} train done! ----------'.format(i))

            n_wins, p_wins, draws = Referee(self.n_player, self.p_player, self.game).play_games(
                self.args.num_arena_compare,
                verbose=False)
            print('new/prev wins : {} / {}, draws : {}'.format(n_wins, p_wins, draws))
            if n_wins + p_wins == 0 or n_wins * 1.0 / (n_wins + p_wins) < self.args.update_threshold:
                """如果新 model 与旧 model 对局胜率不能超过 update_threshold 则不接受"""
                print('rejecting new model...')
                self.nnet.load_checkpoint(folder=self.args.checkpoint_folder, filename='tmp.pth.tar')
            else:
                print('accepting new model...')
                self.nnet.save_checkpoint(folder=self.args.checkpoint_folder,
                                          filename='checkpoint_{}.pth.tar'.format(i))
                self.nnet.save_checkpoint(folder=self.args.checkpoint_folder,
                                          filename='best.pth.tar')


if __name__ == '__main__':
    # 设置 GPU 按需使用，TEST
    set_gpu_memory_grow()
    #
    g = Game(8)
    # nnet = NNet(g, default_args)
    # if default_args.load_model:
    #     nnet.load_checkpoint(folder=default_args.load_folder_file[0], filename=default_args.load_folder_file[1])
    # coach = Coach(g, nnet, default_args)
    # coach.start_learn()
    print('start')

    import multiprocessing

    #
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=default_args.num_self_play_pool)
    coach = Coach(g, default_args)
    result = []
    for i in range(default_args.num_self_play_pool):
        result.append(pool.apply_async(coach.async_execute_episode, args=(g, default_args)))
    pool.close()  # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
    pool.join()  # 等待进程池中的所有进程执行完毕
    print("Sub-process(es) done.")

    for res in result:
        print(res.get())
    print('The End')
