from src.lib.utils import DotDict
import torch.cuda

default_args = DotDict({
    'simulation_count': 20,  # MCTS 模拟次数
    'cpuct': 1,  # MCTS 探索程度
    'lr': 0.001,  # learning rate
    'dropout': 0.3,  # dropout
    'epochs': 10,
    'batch_size': 64,
    'cuda': torch.cuda.is_available(),
    'num_channels': 512,

    'num_iteration': 10,  # 1000,  # 训练迭代次数
    'num_episode': 5,  # 100,  # 每次迭代执行 num_episode 次模拟对局
    # 'temp_threshold': 15,
    'update_threshold': 0.6,  # 更新阈值，超过该值更新神经网络
    'num_iteration_train_examples': 200000,
    # 'numMCTSSims': 25,
    'num_arena_compare': 5,  # 40,
    'num_train_examples_history': 20,

    'checkpoint_folder': '../data/',
    'load_model': True,
    'load_folder_file': ('../data/', 'best.pth.tar'),

    'num_self_play_pool': 2,
    'num_test_play_pool': 4,
})
