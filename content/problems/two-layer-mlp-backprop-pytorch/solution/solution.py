import torch
import torch.nn.functional as F


def mlpBackprop(X, y, W1, b1, W2, b2):
    params = [t.detach().requires_grad_(True) for t in (W1, b1, W2, b2)]
    w1, c1, w2, c2 = params
    hidden = torch.relu(X @ w1 + c1)          # relu's gradient at exactly 0 is 0
    loss = F.cross_entropy(hidden @ w2 + c2, y)
    grads = torch.autograd.grad(loss, params)
    return [loss.detach(), *grads]
