from src.games.game import Game


class Player():
    """
    定义一个玩家类接口
    """

    def __init__(self, game, player_id, description=""):
        self.game = game
        self.player_id = player_id
        self.description = description

    def play(self, board=None):
        pass
