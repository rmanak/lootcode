import torch
import torch.nn.functional as F


def layerNormForwardBackward(x, gamma, beta, dy, eps):
    # Library forward + autograd backward: independent of the numpy version.
    x, gamma, beta = (t.detach().clone().requires_grad_(True) for t in (x, gamma, beta))
    y = F.layer_norm(x, (x.shape[1],), gamma, beta, eps)
    y.backward(dy)
    return [y.detach(), x.grad, gamma.grad, beta.grad]
