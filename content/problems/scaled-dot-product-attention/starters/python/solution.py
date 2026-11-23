import numpy as np


def scaledDotProductAttention(Q, K, V, mask):
    """Masked scaled dot-product attention.

    Args:
        Q: list of lists of floats, shape (num_queries, d_k). Queries.
        K: list of lists of floats, shape (num_keys, d_k). Keys.
        V: list of lists of floats, shape (num_keys, d_v). Values.
        mask: list of lists of ints, shape (num_queries, num_keys). 1 = query i
            may attend to key j, 0 = it may not.

    Returns:
        A list [output, weights] (a tuple works too):
            output: np.ndarray of floats. The attention output.
            weights: np.ndarray of floats. The attention weights.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
