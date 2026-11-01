import numpy as np


def scaledDotProductAttention(Q, K, V, mask):
    """Q: n rows of dk numbers. K: m rows of dk numbers. V: m rows of dv numbers.
    mask: n rows of m entries, 1 = query i may attend to key j, 0 = it may not.
    Return [output, weights] (numpy arrays are fine)."""
    pass
