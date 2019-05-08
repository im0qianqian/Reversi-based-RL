import json
import sys
from src.games.reversi.reversi_game import ReversiGame
from src.games.reversi.reversi_player import ReversiRLPlayer


def short_time_mode():
    """
    短时运行模式
    """

    def init_board():
        full_input = json.loads(input())
        requests = full_input["requests"]
        responses = full_input["responses"]
        color = 1
        if requests[0]['x'] >= 0:
            color = -1
            action_tmp = requests[0]['x'] * game.n + requests[0]['y']
            game.get_next_state(-color, action_tmp, game.get_current_state())
        turn = len(responses)
        for i in range(turn):
            action_tmp = responses[i]['x'] * game.n + responses[i]['y']
            game.get_next_state(color, action_tmp, game.get_current_state())

            action_tmp = requests[i + 1]['x'] * game.n + requests[i + 1]['y']
            game.get_next_state(-color, action_tmp, game.get_current_state())
        return color

    game = ReversiGame(8)
    my_color = init_board()

    player = ReversiRLPlayer(game, choice_mode=0, check_point=['data', 'best.pth.tar'])

    action = player.play(game.get_relative_state(player=my_color, board=game.get_current_state()))[0]

    if 0 <= action < game.n ** 2:
        x, y = int(action // game.n), int(action % game.n)
    else:
        x, y = -1, -1
    print(json.dumps({"response": {"x": x, "y": y}}))


def long_time_mode():
    """
    长时运行模式
    """

    def get_requests_action(requests):
        action_tmp = -1
        if requests['x'] >= 0:
            action_tmp = requests['x'] * game.n + requests['y']
        return action_tmp

    def put_response(action_tmp):
        if 0 <= action_tmp < game.n ** 2:
            x, y = int(action_tmp // game.n), int(action_tmp % game.n)
        else:
            x, y = -1, -1
        print(json.dumps({"response": {"x": x, "y": y}}))
        print('>>>BOTZONE_REQUEST_KEEP_RUNNING<<<')
        sys.stdout.flush()

    game = ReversiGame(8)
    board = game.get_current_state()

    # 第一回合确定己方颜色
    my_color = 1
    action = get_requests_action(json.loads(input())["requests"][0])
    if action != -1:
        my_color = -1
        board, _ = game.get_next_state(-my_color, action, board)

    # 加载 RL 玩家
    player = ReversiRLPlayer(game, choice_mode=0, check_point=['data', 'best.pth.tar'])
    # 初始化颜色
    player.init(my_color)

    # 执行一次操作
    action = player.play(game.get_relative_state(player=my_color, board=board))[0]
    board, _ = game.get_next_state(my_color, action, board)
    put_response(action)
    try:
        while True:
            # 对方
            action = get_requests_action(json.loads(input()))
            board, _ = game.get_next_state(-my_color, action, board)

            # 己方
            action = player.play(game.get_relative_state(player=my_color, board=board))[0]
            board, _ = game.get_next_state(my_color, action, board)
            put_response(action)
    except EOFError:
        pass


if __name__ == '__main__':
    # 开启长时运行模式
    # long_time_mode()
    short_time_mode()
