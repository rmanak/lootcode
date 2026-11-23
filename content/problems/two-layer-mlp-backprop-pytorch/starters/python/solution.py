import torch


def mlpBackprop(X, y, W1, b1, W2, b2):
    """X: (N, D), W1: (D, H), b1: (H,), W2: (H, C), b2: (C,) float64 tensors;
    y: (N,) int64 tensor of labels.
    Return [L, dW1, db1, dW2, db2]: L a 0-dim float64 tensor, each gradient
    shaped like its parameter."""
    pass
