import math

import torch


def distanceDecayAttention(Q, K, V, slopes, causal):
    n, D = Q.shape
    H = slopes.shape[0]
    dh = D // H

    def heads(M):                                   # (n, D) -> (H, n, dh)
        return M.view(n, H, dh).transpose(0, 1)

    idx = torch.arange(n)
    dist = (idx[:, None] - idx[None, :]).abs().to(Q.dtype)
    s = heads(Q) @ heads(K).transpose(-2, -1) / math.sqrt(dh)
    s = s - slopes.to(Q.dtype)[:, None, None] * dist
    if causal:
        s = s.masked_fill(idx[None, :] > idx[:, None], float("-inf"))
    return (torch.softmax(s, dim=-1) @ heads(V)).transpose(0, 1).reshape(n, D)
