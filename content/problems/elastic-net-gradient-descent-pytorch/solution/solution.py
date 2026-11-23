import torch


def elasticNetGD(X, y, alpha, l1Ratio, lr, steps):
    n = X.shape[0]
    l1, l2 = alpha * l1Ratio, alpha * (1.0 - l1Ratio)
    w = torch.zeros(X.shape[1], dtype=X.dtype, requires_grad=True)
    b = torch.zeros((), dtype=X.dtype, requires_grad=True)
    history = []
    for _ in range(steps):
        r = X @ w + b - y
        # abs' gradient at exactly 0 is 0 in autograd: the statement's sign(0) = 0
        J = (r @ r) / (2 * n) + l1 * w.abs().sum() + 0.5 * l2 * (w @ w)
        gw, gb = torch.autograd.grad(J, (w, b))
        history.append(J.detach())
        with torch.no_grad():
            w = (w - lr * gw).requires_grad_(True)
            b = (b - lr * gb).requires_grad_(True)
    return [w.detach(), b.detach(), torch.stack(history)]
