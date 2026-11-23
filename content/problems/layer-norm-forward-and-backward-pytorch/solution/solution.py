import torch


def layerNormForwardBackward(x, gamma, beta, dy, eps):
    # The forward as plain tensor ops, the backward by autograd: independent of
    # the numpy version's hand-derived gradient. Not F.layer_norm: its fused
    # backward kernel loses ~1e-7 to cancellation when eps is tiny and a row is
    # constant (rstd ~ 1e6), where the exact dx is 0 — too noisy for an oracle.
    x, gamma, beta = (t.detach().clone().requires_grad_(True) for t in (x, gamma, beta))
    mu = x.mean(dim=1, keepdim=True)
    xc = x - mu
    var = (xc * xc).mean(dim=1, keepdim=True)       # two-pass: no cancellation
    y = gamma * (xc / torch.sqrt(var + eps)) + beta
    y.backward(dy)
    return [y.detach(), x.grad, gamma.grad, beta.grad]
