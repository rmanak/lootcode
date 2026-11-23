import torch
import torch.nn.functional as F


def batchNormTrain(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    x, gamma, beta = (t.detach().requires_grad_(True) for t in (x, gamma, beta))
    rm, rv = runningMean.clone(), runningVar.clone()   # batch_norm updates them in place
    y = F.batch_norm(x, rm, rv, gamma, beta, training=True, momentum=momentum, eps=eps)
    dx, dgamma, dbeta = torch.autograd.grad(y, (x, gamma, beta), dy)
    return [y.detach(), dx, dgamma, dbeta, rm, rv]
