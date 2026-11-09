import numpy as np


def distanceDecayAttention(Q, K, V, slopes, causal):
    """Multi-head attention with an ALiBi bias of -slopes[h] * |i - j|. Return the n x D output."""
    pass
