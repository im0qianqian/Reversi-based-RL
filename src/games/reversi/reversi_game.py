import numpy as np
from src.games.game import Game
from src.games.reversi.reversi_logic import ReversiLogic


class ReversiGame(Game):
    """
    定义一个游戏类的接口，其他各类游戏可实现它
    """

    def __init__(self, n=8):
        self.n = n  # 棋盘大小 n*n
        self.logic = ReversiLogic(self.n)

    def init(self, board=None):
        """使用棋盘矩阵初始化"""
        self.logic.set_pieces(board)

    def display(self, board=None):
        """打印当前棋盘状态"""
        self.logic.set_pieces(board)
        self.logic.display()

    def get_winner(self, board=None):
        """获取游戏是否结束等"""
        self.logic.set_pieces(board)

        if len(self.logic.get_legal_moves(1)):  # 玩家 1 可走
            return self.WinnerState.GAME_RUNNING
        if len(self.logic.get_legal_moves(-1)):  # 玩家 -1 可走
            return self.WinnerState.GAME_RUNNING

        player1_count = self.logic.count(1)  # player1 得分
        player2_count = self.logic.count(-1)  # player2 得分
        # 比较两个玩家判断哪个赢
        if player1_count == player2_count:  # 平局
            return self.WinnerState.DRAW
        elif player1_count > player2_count:  # player1 胜利
            return self.WinnerState.PLAYER1_WIN
        else:
            return self.WinnerState.PLAYER2_WIN

    def get_current_state(self, board=None):
        """获取当前棋盘状态"""
        self.logic.set_pieces(board)
        return self.logic.pieces

    def get_legal_moves(self, player, board=None):
        """获取行动力矩阵"""
        self.logic.set_pieces(board)
        legal_moves = self.logic.get_legal_moves(player)
        res = np.zeros(self.logic.pieces.shape, dtype=np.int)
        for x, y in legal_moves:
            res[x][y] = 1
        return res

    def get_next_state(self, player, action, board=None):
        """玩家 player 执行 action 后的棋盘状态"""
        self.logic.set_pieces(board)
        if 0 <= action < self.n ** 2:
            self.logic.execute_move((action // self.n, action % self.n), player)
        return self.logic.pieces, -player


if __name__ == "__main__":
    a = ReversiGame(8)
    b = a.get_legal_moves(1)
    print(b.reshape(1, -1))
    # player = 1
    # while True:
    #     a.display()
    #     print(a.board.get_legal_moves(player))
    #     x, y = map(int, input().split())
    #     tmp, player = a.get_next_state(player, x * 8 + y)
    #     pass
    # print(a.get_legal_moves(1))
    # a.display()
