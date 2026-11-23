import torch


def rankingLossAndGrad(preferences, w):
    """preferences: (N, 2, d) float64 tensor (pair i is preferences[i, 0] over
    preferences[i, 1]); w: (d,) float64 tensor.
    Return [L, grad]: L a 0-dim float64 tensor, grad a (d,) float64 tensor."""
    pass
