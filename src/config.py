from src.lib.utils import DotDict
import os

project_root_path = 'C:/Users/qianqian/Documents/GitHub/Reversi-based-RL'
# project_root_path = '/content/gdrive/My Drive/Reversi-based-RL'

default_args = DotDict({
    'simulation_count': 50,  # MCTS 模拟次数
    'cpuct': 1,  # MCTS 探索程度
    'lr': 0.001,  # learning rate
    'dropout': 0.3,  # dropout
    'epochs': 10,
    'batch_size': 64,
    'model_batch_size': 64,  # 模型 batch_size，可用于 TPU 加速
    'num_channels': 512,

    'use_tpu': False,  # 使用 TPU，记得将 batch_size 增大 8 倍
    'use_multiprocessing': False,  # 是否使用多进程模式，可能有些地方不允许创建进程

    'iteration_start': 34,  # 迭代起始数字
    'num_iteration': 1000,  # 训练迭代次数
    'num_episode': 100,  # 每次迭代执行 num_episode 次模拟对局，最好是 num_self_play_pool 的整数倍
    # 'temp_threshold': 15,
    'update_threshold': 0.6,  # 更新阈值，超过该值更新神经网络
    'num_iteration_train_examples': 200000,
    'num_arena_compare': 40,
    'num_train_examples_history': 20,  # train examples 历史记录条数

    'checkpoint_folder': os.path.join(project_root_path, './data/'),  # 模型文件夹
    'load_model': True,
    'train_folder_file': 'train.pth.tar',  # 临时 train 模型文件名
    'best_folder_file': 'best.pth.tar',  # 最优模型文件名

    'logs_folder': os.path.join(project_root_path, './data/logs/'),  # log 文件夹

    'num_self_play_pool': 2,  # 模拟游戏时的进程个数
    'num_test_play_pool': 2,  # 执行测试时的进程个数
})
