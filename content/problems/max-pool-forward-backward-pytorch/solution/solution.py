import torch
import torch.nn.functional as F


def maxPool(x, dout, kernel, stride):
    x = x.detach().requires_grad_(True)
    out = F.max_pool2d(x[None], kernel_size=tuple(kernel), stride=stride)[0]
    (dx,) = torch.autograd.grad(out, x, dout)
    return [out.detach(), dx]
