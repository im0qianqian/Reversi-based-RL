import numpy as np
import collections


class MCTS():
    """
    唔～ 这里是蒙特卡罗树的实现
    """

    def __init__(self, game, nnet):
        self.game = game
        self.nnet = nnet
        self.args = {
            'simulation_count': 20,  # MCTS 模拟次数
            'cpuct': 1,  # 探索程度
        }

        self.Qsa = collections.defaultdict(float)  # 在状态 s 时执行动作 a 的期望回报
        self.Nsa = collections.defaultdict(float)  # s -> a 边的出现次数
        self.Ps = collections.defaultdict(float)  # 从状态 s 开始行动的策略估计值
        self.Ns = collections.defaultdict(float)  # 状态 s 的出现次数
        self.valid_state = {}  # 某一个状态的可行走法，每个元素是一个 np.ndarray

        pass

    def mcts_search(self, relative_board):
        """
        一次 MCTS 搜索
        """
        # 当前状态转化为 str，便于当键
        state = relative_board.tostring()

        # a terminal state, 直接返回结果
        is_win = self.game.get_winner(relative_board)
        if is_win != self.game.WinnerState.GAME_RUNNING:
            return -is_win

        # 如果当前状态没有出现过
        if state not in self.Ps:
            # 这里从神经网络中获得预测
            self.Ps[state], v = self.nnet.predict(state)

            valid_move = self.game.get_legal_moves(1, relative_board).reshape(-1)
            self.valid_state[state] = valid_move

            self.Ps[state] *= valid_move
            sum_Pss = np.sum(self.Ps[state])

            if sum_Pss > 0:
                self.Ps[state] /= sum_Pss
            else:
                print("All valid moves were masked, do workaround.")
                self.Ps[state] += valid_move
                self.Ps[state] /= np.sum(self.Ps[state])

            self.Ns[state] = 0
            """do somethings"""
            return -v
        else:
            # 如果当前状态已经在搜索树中出现过，这里使用 valid_state 记忆一些信息，避免重复请求
            valid_move = self.valid_state[state]

            # 初始化两个待求参数
            max_u, best_action = float('-inf'), -1

            for action in range(self.game.n ** 2):
                if valid_move[action]:
                    """
                    Q-values 上限
                    Latex: $U(s,a) = Q(s,a) + c_{puct}\cdot P(s,a)\cdot\frac{\sqrt{\Sigma_b N(s,b)}}{1+N(s,a)}$
                    """
                    u = self.Qsa[(state, action)] + self.args['cpuct'] * self.Ps[state][action] * self.Ns[
                        state] ** .5 / (
                                1.0 + self.Nsa[(state, action)])

                    if u > max_u:
                        max_u = u
                        best_action = action

            next_state, next_player = self.game.get_next_state(1, best_action, relative_board)
            v = self.mcts_search(self.game.get_relative_state(next_player, next_state))

            # Qsa 怎么算的？？？
            self.Qsa[(state, best_action)] = (self.Nsa[(state, best_action)] * self.Qsa[(state, best_action)] + v) / (
                    self.Nsa[(state, best_action)] + 1.0)
            # 边 s -> a ++
            self.Nsa[(state, best_action)] += 1
            # point state ++
            self.Ns[state] += 1
            return -v
