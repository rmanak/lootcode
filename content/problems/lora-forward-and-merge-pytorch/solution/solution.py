import math

import torch


def loraForward(X, W, A, B, alpha, useRsLora):
    r = A.shape[1]
    scaling = alpha / math.sqrt(r) if useRsLora else alpha / r
    merged = torch.addmm(W, A, B, alpha=scaling)   # W + scaling * A @ B
    return [X @ merged, merged]
