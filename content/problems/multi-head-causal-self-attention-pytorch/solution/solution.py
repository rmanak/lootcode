import math

import torch


def multiHeadSelfAttention(X, Wq, Wk, Wv, Wo, numHeads):
    T, D = X.shape
    dh = D // numHeads

    def heads(M):                                   # (T, D) -> (numHeads, T, dh)
        return M.view(T, numHeads, dh).transpose(0, 1)

    Q, K, V = heads(X @ Wq), heads(X @ Wk), heads(X @ Wv)
    s = Q @ K.transpose(-2, -1) / math.sqrt(dh)
    future = torch.ones(T, T, dtype=torch.bool).triu(1)
    w = torch.softmax(s.masked_fill(future, float("-inf")), dim=-1)
    return (w @ V).transpose(0, 1).reshape(T, D) @ Wo
