import torch


def layerNormForwardBackward(x, gamma, beta, dy, eps):
    """x, dy: (N, D) float64 tensors; gamma, beta: (D,) float64 tensors; eps: float.
    Return [y, dx, dgamma, dbeta] as float64 tensors."""
    pass
