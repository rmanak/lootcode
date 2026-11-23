import torch


def scaledDotProductAttention(Q, K, V, mask):
    """Q: (n, dk), K: (m, dk), V: (m, dv) float tensors; mask: (n, m) int64 tensor of 0/1.
    Return [output, weights]: (n, dv) and (n, m) tensors in Q's dtype."""
    pass
