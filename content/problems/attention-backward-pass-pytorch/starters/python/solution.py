import torch


def attentionBackward(Q, K, V, dO, causal):
    """Q: (n, d), K: (m, d), V: (m, dv), dO: (n, dv) float64 tensors; causal: bool.
    Return [O, dQ, dK, dV] as float64 tensors."""
    pass
