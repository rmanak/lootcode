import torch
import torch.nn.functional as F


def _kl(a, b):
    # F.kl_div(input=log b, target=a) sums a * (log a - log b), with 0 log 0 = 0.
    log_b = torch.where(b > 0, b.log(), torch.zeros_like(b))
    return F.kl_div(log_b, a, reduction="sum")


def divergences(p, q):
    P, Q = p / p.sum(), q / q.sum()
    M = (P + Q) / 2
    return torch.stack([_kl(P, Q), _kl(Q, P), (_kl(P, M) + _kl(Q, M)) / 2])
