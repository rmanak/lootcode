import math

import torch


def groupedQueryAttention(X, Wq, Wk, Wv, Wo, numHeads, numKvHeads):
    T, D = X.shape
    dh = D // numHeads
    group = numHeads // numKvHeads

    def heads(M, n):                                # (T, n * dh) -> (n, T, dh)
        return M.view(T, n, dh).transpose(0, 1)

    Q = heads(X @ Wq, numHeads)
    K = heads(X @ Wk, numKvHeads).repeat_interleave(group, dim=0)
    V = heads(X @ Wv, numKvHeads).repeat_interleave(group, dim=0)
    s = Q @ K.transpose(-2, -1) / math.sqrt(dh)
    future = torch.ones(T, T, dtype=torch.bool).triu(1)
    w = torch.softmax(s.masked_fill(future, float("-inf")), dim=-1)
    return (w @ V).transpose(0, 1).reshape(T, D) @ Wo
