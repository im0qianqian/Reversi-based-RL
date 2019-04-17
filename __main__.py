import json
import time
from src.games.reversi.reversi_game import ReversiGame
from src.games.reversi.reversi_player import ReversiRLPlayer


def init_board(game):
    full_input = json.loads(input())
    requests = full_input["requests"]
    responses = full_input["responses"]
    my_color = 1
    if requests[0]['x'] >= 0:
        my_color = -1
        action = requests[0]['x'] * game.n + requests[0]['y']
        game.get_next_state(-my_color, action, game.get_current_state())
    turn = len(responses)
    for i in range(turn):
        action = responses[i]['x'] * game.n + responses[i]['y']
        game.get_next_state(my_color, action, game.get_current_state())

        action = requests[i + 1]['x'] * game.n + requests[i + 1]['y']
        game.get_next_state(-my_color, action, game.get_current_state())
    return my_color


def short_time_mode():
    """
    短时运行模式
    """
    game = ReversiGame(8)
    my_color = init_board(game)

    player = ReversiRLPlayer(game, ['data', '8x8_100checkpoints_best.pth.tar'])
    player.init(my_color)

    action = player.play(game.get_current_state())

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
        action = -1
        if requests['x'] >= 0:
            action = requests['x'] * game.n + requests['y']
        return action

    def put_response(action):
        if 0 <= action < game.n ** 2:
            x, y = int(action // game.n), int(action % game.n)
        else:
            x, y = -1, -1
        print(json.dumps({"response": {"x": x, "y": y}}))
        print('>>>BOTZONE_REQUEST_KEEP_RUNNING<<<')

    game = ReversiGame(8)
    board = game.get_current_state()

    # 第一回合确定己方颜色
    my_color = 1
    action = get_requests_action(json.loads(input())["requests"][0])
    if action != -1:
        my_color = -1
        board, _ = game.get_next_state(-my_color, action, board)

    # 加载 RL 玩家
    player = ReversiRLPlayer(game, ['data', '8x8_100checkpoints_best.pth.tar'])
    # 初始化颜色
    player.init(my_color)

    # 执行一次操作
    action = player.play(board)
    board, _ = game.get_next_state(my_color, action, board)
    put_response(action)
    try:
        while True:
            # 对方
            action = get_requests_action(json.loads(input()))
            board, _ = game.get_next_state(-my_color, action, board)

            # 己方
            action = player.play(board)
            board, _ = game.get_next_state(my_color, action, board)
            put_response(action)
    except EOFError:
        pass


if __name__ == '__main__':
    long_time_mode()
