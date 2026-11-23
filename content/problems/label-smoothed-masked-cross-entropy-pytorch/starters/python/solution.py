import torch


def smoothedMaskedCrossEntropy(logits, targets, mask, smoothing):
    """logits: (N, C) float32 tensor; targets: (N,) int64 tensor;
    mask: (N,) int64 tensor of 0/1; smoothing: float.
    Return [L, grad]: L a 0-dim float32 tensor, grad an (N, C) float32 tensor."""
    pass
