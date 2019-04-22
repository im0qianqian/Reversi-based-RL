from src.games.game import Game


class Player(object):
    """
    定义一个玩家类接口
    """

    def __init__(self, game, description=""):
        self.game = game
        self.description = description
        self.player_id = None
        self.referee = None

    def init(self, player_id, referee=None):
        """
        用来初始化一些参数
        :param player_id: 黑棋 1 白棋 -1
        :param referee: 指挥者，可从指挥者获取部分信息
        """
        self.player_id = player_id
        self.referee = referee
        pass

    def play(self, board):
        """
        玩家在当前棋盘中走一步
        :param board: 要更新的棋盘
        :return: 下一步的行动位置，-1 代表不行动
        """
        pass
