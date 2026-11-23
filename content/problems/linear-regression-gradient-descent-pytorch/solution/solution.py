import torch
import torch.nn.functional as F


def linearRegressionGD(X, y, lr, steps):
    w = torch.zeros(X.shape[1], dtype=X.dtype, requires_grad=True)
    b = torch.zeros((), dtype=X.dtype, requires_grad=True)
    history = []
    for _ in range(steps):
        loss = F.mse_loss(X @ w + b, y)             # plain mean, so the gradient has the factor 2
        gw, gb = torch.autograd.grad(loss, (w, b))
        history.append(loss.detach())
        with torch.no_grad():
            w = (w - lr * gw).requires_grad_(True)
            b = (b - lr * gb).requires_grad_(True)
    return [w.detach(), b.detach(), torch.stack(history)]
