from src.games.reversi.reversi_player import *
from src.games.reversi.reversi_game import ReversiGame


class Referee():
    """
    这是一个裁判类，指挥游戏的正常运行
    """

    def __init__(self, player1, player2, game):
        self.player1 = player1  # player1 是先手
        self.player2 = player2  # player2 是后手
        self.game = game  # 当前游戏
        self.__board = []  # 棋盘所有过程，可用于悔棋
        self.__action_list = []
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
        player = [self.player2, None, self.player1]
        while game.get_winner() == 0:
            print(player[current_player + 1].description)
            self.game.display()
            action = player[current_player + 1].play()

            self.__action_list.append(action)
            if action != -1:
                legal_moves = self.game.get_legal_moves(current_player)
                assert legal_moves[action // self.game.n][action % self.game.n] == 1
            _, current_player = self.game.get_next_state(current_player, action)
            self.__board.append(_)
        self.game.display()
        print("黑棋胜利！" if game.get_winner() == 1 else "白棋胜利！")


if __name__ == "__main__":
    game = ReversiGame(8)
    # game.init([[1, 0, 1, 1, 0, -1, 0, 0],
    #            [1, 1, -1, 1, -1, -1, 0, 0],
    #            [1, 0, -1, 1, 1, -1, 0, 0],
    #            [0, 0, -1, -1, 1, 1, 0, 0],
    #            [0, 0, -1, -1, -1, 0, 0, 0],
    #            [0, 0, 0, 0, 0, -1, -1, 0],
    #            [0, 0, 0, 0, 0, 0, -1, 0],
    #            [0, 0, 0, 0, 0, 0, 0, 0]])
    # game.display()
    # print(game.get_legal_moves(-1))
    # game.get_next_state(-1, 4)
    # game.display()
    human1 = ReversiRandomPlayer(game, 1, "黑棋")
    human2 = ReversiBotzonePlayer(game, -1, "白棋")
    referee = Referee(human1, human2, game)
    human2.referee = referee
    referee.start_game()
    pass
