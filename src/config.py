from src.lib.utils import DotDict
import torch.cuda

default_mcts_args = DotDict({
    'simulation_count': 20,  # MCTS 模拟次数
    'cpuct': 1,  # 探索程度
})

default_nnet_args = DotDict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': torch.cuda.is_available(),
    'num_channels': 512
})
