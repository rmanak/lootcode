import math

import torch


def attentionBackward(Q, K, V, dO, causal):
    Q, K, V = (t.detach().requires_grad_(True) for t in (Q, K, V))
    S = Q @ K.T / math.sqrt(Q.shape[1])
    if causal:
        S = S.masked_fill(torch.ones_like(S, dtype=torch.bool).triu(1), float("-inf"))
    O = torch.softmax(S, dim=-1) @ V
    dQ, dK, dV = torch.autograd.grad(O, (Q, K, V), dO)
    return [O.detach(), dQ, dK, dV]
