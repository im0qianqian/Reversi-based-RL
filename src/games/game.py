class Game():
    """
    定义一个游戏类的接口，其他各类游戏可实现它
    适用于：双人对战、回合制游戏，如棋类游戏
    玩家：1 与 -1 代表双方，0 代表空位
    """

    def init(self):
        "游戏状态初始化"
        pass

    def display(self, board=None):
        "打印当前游戏状态（棋盘）"
        pass

    def get_winner(self, board=None):
        """
        游戏是否已经结束

        Input:
            board: 棋盘，为 None 代表使用已创建的棋盘
        Output:
            0 代表游戏未结束
            1 代表玩家 1 赢得比赛
            -1 代表玩家 -1 赢得比赛
        """
        pass

    def get_current_state(self, board=None):
        "获取当前棋盘状态"
        pass

    def get_next_state(self, player, action, board=None):
        """
        获取在action执行完以后的棋盘状态

        Input:
            player: 当前用户
            action: 执行的动作
            board: 棋盘，为 None 代表使用已创建的棋盘
        """
        pass

    def get_legal_moves(self, player, board=None):
        """
        获取下一步合法的方案

        Input:
            player: 当前用户
            board: 棋盘，为 None 代表使用已创建的棋盘
        """
        pass