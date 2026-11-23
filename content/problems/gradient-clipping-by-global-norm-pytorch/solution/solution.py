import torch


def clipGradients(grads, maxNorm):
    flat = torch.cat([g.reshape(-1) for g in grads])
    big = flat.abs().max()
    # Scale before squaring: entries near 1e200 would overflow vector_norm.
    norm = big * torch.linalg.vector_norm(flat / big) if big > 0 else big
    if norm > maxNorm:
        grads = [g * (maxNorm / norm) for g in grads]
    return [grads, norm]
