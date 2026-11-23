import torch
import torch.nn.functional as F


def smoothedMaskedCrossEntropy(logits, targets, mask, smoothing):
    z = logits.detach().requires_grad_(True)
    m = mask.to(z.dtype)
    count = m.sum()
    if count == 0:
        return [torch.zeros((), dtype=z.dtype), torch.zeros_like(logits)]
    per_position = F.cross_entropy(z, targets, reduction="none", label_smoothing=smoothing)
    loss = (per_position * m).sum() / count
    (grad,) = torch.autograd.grad(loss, z)
    return [loss.detach(), grad]
