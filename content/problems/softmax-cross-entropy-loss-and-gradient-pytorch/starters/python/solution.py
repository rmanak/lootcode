import torch


def softmaxCrossEntropy(logits, labels):
    """logits: (N, C) float tensor; labels: (N,) int64 tensor.
    Return [L, grad]: a 0-dim tensor and an (N, C) tensor, in logits' dtype."""
    pass
