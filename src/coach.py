from src.referee import Referee
from src.games.reversi.reversi_game import ReversiGame as Game
from src.games.reversi.reversi_player import *
from src.config import *
from src.lib.utils import *
from collections import deque
from src.games.reversi.reversi_nnet import NNetWrapper as NNet
import multiprocessing
import os
import shutil


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
        result = referee.play_game(verbose=False)
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

    def async_execute_episode(self, idx, process_episode_num=1):
        """
        考虑到神经网络初始化的过程比较耗时
        因此我们定义 process_episode_num 代表每一个进程执行的轮次（如 32 次并发在 4 核中，process_episode_num 可以是 32/4=8）
            idx: 进程号（循环变量 i）
            process_episode_num: 该进程执行的次数
        """
        set_gpu_memory_grow()
        player = ReversiRLPlayer(self.game, choice_mode=1, check_point=self.args.load_folder_file, args=self.args)

        episode_time = time.time()
        train_examples_tmp = []
        for _ in range(process_episode_num):
            train_examples_tmp += self.execute_episode(self.game, player, player)
            print('execute episode in process {} : {} / {}, episode time: {}'.format(idx, _ + 1, process_episode_num,
                                                                                     time.time() - episode_time))
            episode_time = time.time()
        return train_examples_tmp

    def parallel_self_play(self):
        """
        并行化的 self play，返回得到的 train_examples_list
        """
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(processes=self.args.num_self_play_pool)

        train_examples_list = deque([], maxlen=self.args.num_iteration_train_examples)

        start_time = time.time()  # 开始执行的时间
        result = []
        for i in range(self.args.num_self_play_pool):  # 开启几个进程执行
            result.append(pool.apply_async(self.async_execute_episode,
                                           args=(i, self.args.num_episode // self.args.num_self_play_pool,)))
        pool.close()  # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
        pool.join()  # 等待进程池中的所有进程执行完毕
        for res in result:
            train_examples_list += res.get()
        print('parallel_self_play done! time: {}s'.format(time.time() - start_time))
        return train_examples_list

    def async_self_test_play(self, idx, process_test_num):
        # 显存按需使用
        set_gpu_memory_grow()
        # 加载新模型玩家
        n_player = ReversiRLPlayer(game=self.game, choice_mode=0, nnet=None, check_point=self.args.train_folder_file,
                                   args=self.args)
        # 加载旧模型玩家
        p_player = ReversiRLPlayer(game=self.game, choice_mode=0, nnet=None, check_point=self.args.best_folder_file,
                                   args=self.args)

        n_wins, p_wins, draws = Referee(n_player, p_player, self.game).play_games(process_test_num, verbose=False)
        print('process: {}, new/prev wins : {} / {}, draws : {}'.format(idx, n_wins, p_wins, draws))
        return n_wins, p_wins, draws

    def parallel_self_test_play(self):
        """
        并行化的 self test play
        """
        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(processes=self.args.num_test_play_pool)

        start_time = time.time()  # 开始执行的时间
        result = []
        for i in range(self.args.num_test_play_pool):  # 开启几个进程执行
            result.append(pool.apply_async(self.async_self_test_play,
                                           args=(i, self.args.num_arena_compare // self.args.num_test_play_pool,)))
        pool.close()  # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
        pool.join()  # 等待进程池中的所有进程执行完毕

        n_wins = p_wins = draws = 0
        for _ in result:
            n_wins_tmp, p_wins_tmp, draws_tmp = _.get()
            n_wins += n_wins_tmp
            p_wins += p_wins_tmp
            draws += draws_tmp
        print(
            'Final new/prev wins : {} / {}, draws : {}, time: '.format(n_wins, p_wins, draws, time.time() - start_time))
        if n_wins + p_wins == 0 or n_wins * 1.0 / (n_wins + p_wins) < self.args.update_threshold:
            """如果新 model 与旧 model 对局胜率不能超过 update_threshold 则不接受"""
            print('rejecting new model...')  # 这里不执行任何动作
        else:
            print('accepting new model... copy train_folder_file to best_folder_file')
            # 复制文件 train_folder_file 到 best_folder_file
            shutil.move(os.path.join(self.args.train_folder_file[0], self.args.train_folder_file[1]),
                        os.path.join(self.args.best_folder_file[0], self.args.best_folder_file[1]))

    def train_network(self):
        nnet = NNet(self.game, self.args)
        # 从最优模型加载
        nnet.load_checkpoint(folder=self.args.checkpoint_folder, filename='best.pth.tar')
        train_examples = []
        for e in self.train_examples_history:
            train_examples.extend(e)
        nnet.train(train_examples)
        # 保存为训练模型
        nnet.save_checkpoint(folder=self.args.checkpoint_folder, filename='train.pth.tar')

    def start_learn(self):
        """学习学习"""
        for i in range(self.args.num_iteration):  # 迭代
            print("----------------- 第 {} 次迭代 ----------------".format(i))
            self.train_examples_history.append(self.parallel_self_play())  # 进行 self-play

            # 使用得到的数据进行训练（这里单进程进行，使用 Process 可以看到显存被释放了，虽然不懂 tf 有没有在自己维护的内部自动释放）
            p = multiprocessing.Process(target=self.train_network)
            p.start()
            p.join()
            # self.train_network()
            print('------- iteration {} train done! ----------'.format(i))

            self.parallel_self_test_play()
            # 我在这里偷偷的拷贝一份没有人知道吧
            shutil.copyfile(os.path.join(self.args.best_folder_file[0], self.args.best_folder_file[1]),
                            os.path.join(self.args.checkpoint_folder, 'checkpoint_{}.pth.tar'.format(i)))
            print('------- iteration {} self-play test done! -----------'.format(i))


if __name__ == '__main__':
    import os

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 这样就不会有 tensorflow 的 log 了
    multiprocessing.freeze_support()
    # 设置 GPU 按需使用，TEST
    # set_gpu_memory_grow()
    #
    g = Game(8)
    coach = Coach(g, default_args)
    coach.start_learn()
    # coach.start_learn()
    # res = coach.parallel_self_play()
