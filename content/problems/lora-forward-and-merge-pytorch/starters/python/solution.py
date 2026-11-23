import torch


def loraForward(X, W, A, B, alpha, useRsLora):
    """X: (N, din), W: (din, dout), A: (din, r), B: (r, dout) float64 tensors;
    alpha: float; useRsLora: bool.
    Return [Y, mergedW]: Y (N, dout) and mergedW (din, dout), float64."""
    pass
