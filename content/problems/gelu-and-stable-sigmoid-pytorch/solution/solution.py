import torch
import torch.nn.functional as F


def activations(x):
    # Library activations + autograd derivatives: independent of the numpy version.
    a = x.detach().clone().requires_grad_(True)
    s = torch.sigmoid(a)
    (ds,) = torch.autograd.grad(s.sum(), a)
    g = a.detach().clone().requires_grad_(True)
    gelu = F.gelu(g, approximate="none")
    (dg,) = torch.autograd.grad(gelu.sum(), g)
    return [s.detach(), ds, F.logsigmoid(x), gelu.detach(), dg]
