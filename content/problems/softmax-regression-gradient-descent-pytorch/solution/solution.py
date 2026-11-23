import torch
import torch.nn.functional as F


def softmaxRegressionGD(X, y, numClasses, lr, steps):
    W = torch.zeros(X.shape[1], numClasses, dtype=X.dtype, requires_grad=True)
    b = torch.zeros(numClasses, dtype=X.dtype, requires_grad=True)
    history = []
    for _ in range(steps):
        loss = F.cross_entropy(X @ W + b, y)        # log-softmax inside: no log(0)
        gW, gb = torch.autograd.grad(loss, (W, b))
        history.append(loss.detach())
        with torch.no_grad():
            W = (W - lr * gW).requires_grad_(True)
            b = (b - lr * gb).requires_grad_(True)
    return [W.detach(), b.detach(), torch.stack(history)]
