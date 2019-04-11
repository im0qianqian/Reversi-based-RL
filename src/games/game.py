from enum import Enum, unique


class Game():
    """
    定义一个游戏类的接口，其他各类游戏可实现它
    适用于：双人对战、回合制游戏，如棋类游戏
    玩家：1 与 -1 代表双方，0 代表空位
    """

    @unique
    class WinnerState(Enum):
        """
        这是一个游戏状态枚举类
            GAME_RUNNING 游戏未结束
            PLAYER1_WIN 玩家 1 胜利
            PLAYER2_WIN 玩家 -1 胜利
            DRAW        平局
        """
        GAME_RUNNING = 0
        PLAYER1_WIN = 1
        PLAYER2_WIN = -1
        DRAW = 2
        pass

    def init(self, board):
        """
        游戏状态初始化
        """
        pass

    def display(self, board):
        """
        打印当前游戏状态（棋盘）
        """
        pass

    def get_winner(self, board):
        """
        游戏是否已经结束

        Input:
            board: 棋盘，为 None 代表使用已创建的棋盘
        Output:
            0 代表游戏未结束
            1 代表玩家 1 赢得比赛
            -1 代表玩家 -1 赢得比赛
            2 代表平局
        """
        pass

    def get_next_state(self, player, action, board):
        """
        获取在action执行完以后的棋盘状态

        Input:
            player: 当前用户
            action: 执行的动作
            board: 棋盘，为 None 代表使用已创建的棋盘
        """
        pass

    def get_current_state(self):
        """
        获取当前棋盘状态
        """
        pass

    def get_relative_state(self, player, board):
        """
        获取相对棋盘矩阵
        :param player: 玩家 id
        :param board: 传入的棋盘矩阵
        :return: 相对棋盘矩阵（假设自己 id 为 1 看到的情景）
        """
        pass

    def get_legal_moves(self, player, board):
        """
        获取下一步合法的方案

        Input:
            player: 当前用户
            board: 棋盘，为 None 代表使用已创建的棋盘
        Output:
            一个矩阵，其中为 1 的代表可行坐标
        """
        pass
