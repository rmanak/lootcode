import torch
import torch.nn.functional as F


def trainRanker(preferences, lr, steps):
    diff = preferences[:, 0, :] - preferences[:, 1, :]      # (N, d), fixed for the run
    w = torch.zeros(diff.shape[1], dtype=diff.dtype, requires_grad=True)
    for _ in range(steps):
        loss = F.softplus(-(diff @ w)).mean()               # log(1 + e^{-m}), overflow-free
        (g,) = torch.autograd.grad(loss, (w,))
        with torch.no_grad():
            w = (w - lr * g).requires_grad_(True)
    return w.detach()
