import torch
import torch.nn.functional as F


def logisticRegressionGD(X, y, lr, steps):
    target = y.to(X.dtype)
    w = torch.zeros(X.shape[1], dtype=X.dtype, requires_grad=True)
    b = torch.zeros((), dtype=X.dtype, requires_grad=True)
    history = []
    for _ in range(steps):
        # the fused log-sigmoid form never takes log(0), however large |z| gets
        loss = F.binary_cross_entropy_with_logits(X @ w + b, target)
        gw, gb = torch.autograd.grad(loss, (w, b))
        history.append(loss.detach())
        with torch.no_grad():
            w = (w - lr * gw).requires_grad_(True)
            b = (b - lr * gb).requires_grad_(True)
    return [w.detach(), b.detach(), torch.stack(history)]
