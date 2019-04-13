import torch
import numpy as np

np_data = np.arange(6).reshape((2, 3))
torch_data = torch.from_numpy(np_data)
tensor2array = torch_data.numpy()
print(
    '\nnumpy array:', np_data,  # [[0 1 2], [3 4 5]]
    '\ntorch tensor:', torch_data,  # 0  1  2 \n 3  4  5    [torch.LongTensor of size 2x3]
    '\ntensor to array:', tensor2array,  # [[0 1 2], [3 4 5]]
)
