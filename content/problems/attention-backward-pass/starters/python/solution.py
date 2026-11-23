import numpy as np


def attentionBackward(Q, K, V, dO, causal):
    """Forward and backward pass of single-head scaled dot-product attention.

    Args:
        Q: list of lists of floats, shape (num_queries, head_dim). Queries.
        K: list of lists of floats, shape (num_keys, head_dim). Keys.
        V: list of lists of floats, shape (num_keys, value_dim). Values.
        dO: list of lists of floats, shape (num_queries, value_dim). Upstream
            gradient dLoss/dO.
        causal: bool. If True, apply a causal mask; num_queries == num_keys
            then.

    Returns:
        A list [O, dQ, dK, dV] (a tuple works too):
            O: np.ndarray of floats. Attention output.
            dQ: np.ndarray of floats. Gradient w.r.t. Q.
            dK: np.ndarray of floats. Gradient w.r.t. K.
            dV: np.ndarray of floats. Gradient w.r.t. V.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
