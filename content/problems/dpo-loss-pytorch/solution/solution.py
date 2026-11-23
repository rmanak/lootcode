import torch
import torch.nn.functional as F


def dpoLoss(policyChosen, policyRejected, refChosen, refRejected, beta, labelSmoothing, lossType):
    pc = policyChosen.detach().requires_grad_(True)
    pr = policyRejected.detach().requires_grad_(True)
    h = (pc - pr) - (refChosen - refRejected)
    if lossType == "sigmoid":
        z = beta * h
        losses = -(1 - labelSmoothing) * F.logsigmoid(z) - labelSmoothing * F.logsigmoid(-z)
    else:  # "ipo"
        losses = (h - 1 / (2 * beta)) ** 2
    loss = losses.mean()
    grad_chosen, grad_rejected = torch.autograd.grad(loss, (pc, pr))
    chosen = beta * (policyChosen - refChosen)
    rejected = beta * (policyRejected - refRejected)
    accuracy = (chosen > rejected).to(chosen.dtype).mean()
    return [loss.detach(), chosen, rejected, accuracy, grad_chosen, grad_rejected]
