import argparse
from src.config import *
from src.games.reversi.reversi_game import ReversiGame as Game
from src.coach import Coach
import pprint
from src.games.reversi.reversi_player import ReversiRandomPlayer, ReversiRLPlayer, ReversiGreedyPlayer, \
    ReversiBotzonePlayer, ReversiHumanPlayer
from src.referee import Referee


def create_parser():
    """
    创建 parser，包含 train mode 以及 run mode
    其中 train mode 因为参数较多，暂添加部分参数，也可以通过修改 config.py 来达到目的
    run mode --vs 接收两个参数，分别是两个玩家的类型
    """
    parser = argparse.ArgumentParser(
        description="Design and Implementation of Othello Based on Reinforcement Learning. by im0qianqian")

    subparser = parser.add_subparsers(help="what do you want to do?")
    train_parser = subparser.add_parser('train')
    train_parser.add_argument("--simu", "--simulation_count", metavar=default_args['simulation_count'],
                              dest='simulation_count',
                              help="MCTS Simulation Count", type=int, default=default_args['simulation_count'])
    train_parser.add_argument("--cpuct", metavar=default_args['cpuct'],
                              dest='cpuct',
                              help="MCTS cpuct", type=float, default=default_args['cpuct'])
    train_parser.add_argument("--lr", "--learning_rate", metavar=default_args['lr'],
                              dest='lr',
                              help="learning rate", type=float, default=default_args['lr'])
    train_parser.add_argument("--bs", "--batch_size", metavar=default_args['batch_size'],
                              dest='batch_size',
                              help="batch size", type=int, default=default_args['batch_size'])
    train_parser.add_argument("--chan", "--num_channels", metavar=default_args['num_channels'],
                              dest='num_channels',
                              help="CNN filter size(channels)", type=int, default=default_args['num_channels'])
    train_parser.add_argument("--epochs", metavar=default_args['epochs'],
                              dest='epochs',
                              help="epochs", type=int, default=default_args['epochs'])
    train_parser.add_argument("--dropout", metavar=default_args['dropout'],
                              dest='dropout',
                              help="fully connected layer dropout", type=float, default=default_args['dropout'])
    train_parser.add_argument(
        "--use_multiprocessing",
        dest="use_multiprocessing",
        help="use multiprocessing (self play)", action="store_false")
    train_parser.add_argument(
        "--use_tpu",
        dest="use_tpu",
        help="use tpu (predict and train network)", action="store_true")
    train_parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="increase output verbosity", action="store_true")

    run_parser = subparser.add_parser('run')
    # run mode --vs 接受两个参数，分别代表 player 的类型，其中第一个参数为先手，第二个为后手
    run_parser.add_argument("--vs", metavar=("human", "rl_player"),
                            dest='player_vs',
                            nargs=2,
                            help="choose from 'human', 'random_player', 'greedy_player', 'rl_player', 'botzone_player'",
                            required=True,
                            choices=['human', 'random_player', 'greedy_player', 'rl_player', 'botzone_player'])
    return parser.parse_args()


def execute_parser(args_dict):
    if 'player_vs' in args_dict:
        # run mode
        game = Game(8)

        def get_player(player_str):
            # 啊啊啊啊啊，我也不想这么干呀，以后再设计设计
            # 千千已经懒到这种地步了嘛 嘤嘤嘤
            if player_str == 'human':
                return ReversiHumanPlayer(game)
            elif player_str == 'greedy_player':
                return ReversiGreedyPlayer(game, greedy_mode=0)
            elif player_str == 'random_player':
                return ReversiRandomPlayer(game)
            elif player_str == 'rl_player':
                return ReversiRLPlayer(game=game, choice_mode=0, nnet=None,
                                       check_point=[default_args.checkpoint_folder,
                                                    default_args.best_folder_file],
                                       args=default_args)
            elif player_str == 'botzone_player':
                return ReversiBotzonePlayer(game)
            # return None 应该是不可能发生的，因为 argparse 中已经设置了 required = True 且做了约束
            return None

        player1 = get_player(args_dict['player_vs'][0])
        player2 = get_player(args_dict['player_vs'][1])
        referee = Referee(player1, player2, game)
        print(referee.play_game(verbose=True))

    else:
        # train mode
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 这样就不会有 tensorflow 的 log 了
        g = Game(8)
        args = default_args
        # 使用指定的参数代替原参数
        for key, value in args_dict.items():
            if key in args:
                args[key] = value
        pprint.pprint(args)
        coach = Coach(g, args)
        coach.start_learn()


if __name__ == "__main__":
    """
    这是几个命令示例，你也可以使用 python -m src.main train --help 查看 train mode 下的详细介绍
    python -m src.main --help
    train: python -m src.main train --simu 5 --lr 0.0001 --bs 128 --epochs 20 --use_multiprocessing
    run: python -m src.main run --vs random_player rl_player
    """
    args = create_parser()
    execute_parser(vars(args))
