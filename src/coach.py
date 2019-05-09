import sys

sys.path.extend(['/content/gdrive/My Drive/Reversi-based-RL_old'])
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
import pickle


class Coach(object):
    """
    reinforcement learning self-play
    """

    def __init__(self, game, args):
        self.game = game
        self.args = args
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
        player = ReversiRLPlayer(self.game, choice_mode=1,
                                 check_point=[self.args.checkpoint_folder, self.args.best_folder_file], args=self.args)

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
        self play，返回得到的 train_examples_list
        """
        train_examples_list = deque([], maxlen=self.args.num_iteration_train_examples)
        start_time = time.time()  # 开始执行的时间

        if self.args.use_multiprocessing:
            multiprocessing.freeze_support()
            pool = multiprocessing.Pool(processes=self.args.num_self_play_pool)

            result = []
            for i in range(self.args.num_self_play_pool):  # 开启几个进程执行
                result.append(pool.apply_async(self.async_execute_episode,
                                               args=(i, self.args.num_episode // self.args.num_self_play_pool,)))
            pool.close()  # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
            pool.join()  # 等待进程池中的所有进程执行完毕
            for res in result:
                train_examples_list += res.get()
        else:
            train_examples_list += self.async_execute_episode(0, self.args.num_episode)

        print('parallel_self_play done! time: {}s'.format(time.time() - start_time))
        return train_examples_list

    def async_self_test_play(self, idx, process_test_num):
        # 显存按需使用
        set_gpu_memory_grow()
        # 加载新模型玩家（从刚刚训练好的 train_folder_file 加载）
        n_player = ReversiRLPlayer(game=self.game, choice_mode=0, nnet=None,
                                   check_point=[self.args.checkpoint_folder, self.args.train_folder_file],
                                   args=self.args)
        # 加载旧模型玩家（旧的 best_folder_file）
        p_player = ReversiRLPlayer(game=self.game, choice_mode=0, nnet=None,
                                   check_point=[self.args.checkpoint_folder, self.args.best_folder_file],
                                   args=self.args)

        n_wins, p_wins, draws = Referee(n_player, p_player, self.game).play_games(process_test_num, verbose=False)
        print('process: {}, new/prev wins : {} / {}, draws : {}'.format(idx, n_wins, p_wins, draws))
        return n_wins, p_wins, draws

    def parallel_self_test_play(self, idx):
        """
        并行化的 self test play
        """
        start_time = time.time()  # 开始执行的时间
        n_wins = p_wins = draws = 0

        if self.args.use_multiprocessing:
            multiprocessing.freeze_support()
            pool = multiprocessing.Pool(processes=self.args.num_test_play_pool)

            result = []
            for i in range(self.args.num_test_play_pool):  # 开启几个进程执行
                result.append(pool.apply_async(self.async_self_test_play,
                                               args=(i, self.args.num_arena_compare // self.args.num_test_play_pool,)))
            pool.close()  # 关闭进程池，表示不能再往进程池中添加进程，需要在join之前调用
            pool.join()  # 等待进程池中的所有进程执行完毕

            for _ in result:
                n_wins_tmp, p_wins_tmp, draws_tmp = _.get()
                n_wins += n_wins_tmp
                p_wins += p_wins_tmp
                draws += draws_tmp
        else:
            n_wins, p_wins, draws = self.async_self_test_play(0, self.args.num_arena_compare)

        print(
            'Final new/prev wins : {} / {}, draws : {}, time: {}'.format(n_wins, p_wins, draws,
                                                                         time.time() - start_time))
        if n_wins + p_wins == 0 or n_wins * 1.0 / (n_wins + p_wins) < self.args.update_threshold:
            """如果新 model 与旧 model 对局胜率不能超过 update_threshold 则不接受"""
            print('rejecting new model...')  # 这里不执行任何动作
        else:
            print('accepting new model... copy train_folder_file to best_folder_file')
            # 我在这里偷偷的拷贝一份没有人知道吧
            shutil.copyfile(os.path.join(self.args.checkpoint_folder, self.args.train_folder_file),
                            os.path.join(self.args.checkpoint_folder, 'checkpoint_{}_update.pth.tar'.format(idx)))

            # 这一步是删除旧版本的 best.pth.tar （其实也可以用下一步的 move 覆盖掉，然而谷歌云盘的历史版本很困扰惹）
            # 好像即使删掉原文件也会记录历史版本，那还是删掉吧
            # os.remove(os.path.join(self.args.checkpoint_folder, self.args.best_folder_file))

            # 复制文件 train_folder_file 到 best_folder_file
            shutil.move(os.path.join(self.args.checkpoint_folder, self.args.train_folder_file),
                        os.path.join(self.args.checkpoint_folder, self.args.best_folder_file))

    def train_network(self):
        nnet = NNet(self.game, self.args)
        # 从最优模型加载
        nnet.load_checkpoint(folder=self.args.checkpoint_folder, filename=self.args.best_folder_file)
        train_examples = []
        for e in self.train_examples_history:
            train_examples.extend(e)
        # 打乱顺序
        np.random.shuffle(train_examples)
        # 开始训练
        nnet.train(train_examples)
        # 保存为训练模型
        nnet.save_checkpoint(folder=self.args.checkpoint_folder, filename=self.args.train_folder_file)

    def parallel_train_network(self, idx):
        train_start_time = time.time()
        if self.args.use_multiprocessing:
            # 使用得到的数据进行训练（这里单进程进行，使用 Process 可以看到显存被释放了，虽然不懂 tf 有没有在自己维护的内部自动释放）
            p = multiprocessing.Process(target=self.train_network)
            p.start()
            p.join()
        else:
            self.train_network()
        print('------- iteration {} train done! time: {}s ----------'.format(idx, time.time() - train_start_time))

    def start_learn(self):
        """学习学习"""
        for i in range(self.args.iteration_start, self.args.iteration_start + self.args.num_iteration):  # 迭代
            print("----------------- 第 {} 次迭代 ----------------".format(i))
            self.train_examples_history.append(self.parallel_self_play())

            # 保存 train_examples 数据
            self.save_train_examples(i)

            # 训练网络
            self.parallel_train_network(i)

            # 测试
            self.parallel_self_test_play(i)
            print('------- iteration {} self-play test done! -----------'.format(i))

    def save_train_examples(self, idx):
        # 存储测试点
        try:
            filename = os.path.join(self.args.checkpoint_folder, 'checkpoint_{}.examples'.format(idx))
            with open(filename, 'wb+') as f:
                pickle.Pickler(f).dump(self.train_examples_history)
            f.close()
        except Exception as e:
            print('save train examples error, ', e)

    def load_train_examples(self, idx):
        # 加载测试点
        try:
            filename = os.path.join(self.args.checkpoint_folder, 'checkpoint_{}.examples'.format(idx))
            with open(filename, 'rb') as f:
                self.train_examples_history += pickle.Unpickler(f).load()
            f.close()
        except Exception as e:
            print('load train examples error, ', e)


if __name__ == '__main__':
    import pprint

    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 这样就不会有 tensorflow 的 log 了
    g = Game(8)
    pprint.pprint(default_args)
    coach = Coach(g, default_args)
    coach.start_learn()
