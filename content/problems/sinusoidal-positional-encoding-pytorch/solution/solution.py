import math

import torch


def positionalEncoding(positions, d, base):
    pos = positions.to(torch.float64)[:, None]                      # (n, 1)
    i = torch.arange(0, d, 2, dtype=torch.float64)                   # 2i for each pair
    angle = pos * torch.pow(torch.tensor(float(base), dtype=torch.float64), -i / d)
    pe = torch.empty(positions.shape[0], d, dtype=torch.float64)
    pe[:, 0::2] = torch.sin(angle)
    pe[:, 1::2] = torch.cos(angle[:, : d // 2])                      # odd d: one fewer cos
    return pe
