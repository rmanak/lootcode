import numpy as np


def attentionBackward(Q, K, V, dO, causal):
    """O = softmax(Q K^T / sqrt(d) + mask) V. Return [O, dQ, dK, dV]."""
    pass
