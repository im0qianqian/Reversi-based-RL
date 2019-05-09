class Player(object):
    """
    定义一个玩家类
    """

    def __init__(self, game, description=""):
        self.game = game
        self.description = description
        # 默认黑棋
        self.referee = None

    def init(self, referee=None):
        """
        用来初始化一些参数
        :param referee: 指挥者，可从指挥者获取部分信息
        """
        self.referee = referee
        pass

    def play(self, board):
        """
        玩家在当前棋盘中走一步及行动概率
        :param board: 要更新的棋盘
        :return: 下一步的行动位置，-1 代表不行动 + 行动概率
        """
        pass
