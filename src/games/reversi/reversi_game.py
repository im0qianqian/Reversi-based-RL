import numpy as np
from src.games.game import Game
from src.games.reversi.reversi_board import ReversiBoard


class ReversiGame(Game):
    """
    定义一个游戏类的接口，其他各类游戏可实现它
    """

    def __init__(self, n=8):
        self.n = n  # 棋盘大小 n*n
        self.board = ReversiBoard(self.n)

    def init(self):
        pass

    def display(self, board=None):
        self.board.set_pieces(board)
        self.board.display()

    def get_winner(self, board=None):
        self.board.set_pieces(board)
        if len(self.board.get_legal_moves(1)):
            return 0
        if len(self.board.get_legal_moves(-1)):
            return 0
        if self.board.count(1) > self.board.count(-1):
            return 1
        return -1

    def get_current_state(self, board=None):
        self.board.set_pieces(board)
        return self.board.pieces

    def get_legal_moves(self, player, board=None):
        self.board.set_pieces(board)
        legal_moves = self.board.get_legal_moves(player)
        res = np.zeros(self.board.pieces.shape, dtype=np.int)
        for x, y in legal_moves:
            res[x][y] = 1
        return res

    def get_next_state(self, player, action, board=None):
        self.board.set_pieces(board)
        if action < 0 or action >= self.n * self.n:
            return (self.board, -player)
        self.board.execute_move((action // self.n, action % self.n), player)
        return (self.board.pieces, -player)


if __name__ == "__main__":
    a = ReversiGame(8)
    player = 1
    while True:
        a.display()
        print(a.board.get_legal_moves(player))
        x, y = map(int, input().split())
        tmp, player = a.get_next_state(player, x * 8 + y)
        pass
    # print(a.get_legal_moves(1))
    # a.display()