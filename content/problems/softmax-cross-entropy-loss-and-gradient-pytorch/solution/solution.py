import torch
import torch.nn.functional as F


def softmaxCrossEntropy(logits, labels):
    # The reference uses the library loss and autograd (the solver may use
    # neither): independent of the numpy version's hand-derived gradient.
    z = logits.detach().clone().requires_grad_(True)
    loss = F.cross_entropy(z, labels)
    loss.backward()
    return [loss.detach(), z.grad]
