import torch
import torch.nn.functional as F


def rankingLossAndGrad(preferences, w):
    weights = w.detach().requires_grad_(True)
    diff = preferences[:, 0, :] - preferences[:, 1, :]
    loss = F.softplus(-(diff @ weights)).mean()     # log(1 + e^-margin)
    (grad,) = torch.autograd.grad(loss, weights)
    return [loss.detach(), grad]
