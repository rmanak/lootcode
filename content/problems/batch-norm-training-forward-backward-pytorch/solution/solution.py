import torch


def batchNormTrain(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    # The forward as plain tensor ops, the backward by autograd: independent of
    # the numpy version's hand-derived gradient. Not F.batch_norm: in float32 its
    # single-threaded CPU backward (the sandbox's) loses ~1e-4 of dgamma to
    # cancellation once a column's mean is ~15x its spread — too noisy for an oracle.
    x, gamma, beta = (t.detach().clone().requires_grad_(True) for t in (x, gamma, beta))
    n = x.shape[0]
    mu = x.mean(dim=0)
    xc = x - mu
    var = (xc * xc).mean(dim=0)                     # biased, two-pass: no cancellation
    y = gamma * (xc / torch.sqrt(var + eps)) + beta
    dx, dgamma, dbeta = torch.autograd.grad(y, (x, gamma, beta), dy)
    with torch.no_grad():
        # PyTorch's convention: the running variance takes the unbiased batch variance.
        rm = (1 - momentum) * runningMean + momentum * mu
        rv = (1 - momentum) * runningVar + momentum * var * n / (n - 1)
    return [y.detach(), dx, dgamma, dbeta, rm, rv]
