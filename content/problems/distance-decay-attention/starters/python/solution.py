import numpy as np


def distanceDecayAttention(Q, K, V, slopes, causal):
    """Multi-head self-attention with a per-head linear distance (ALiBi) bias.

    Args:
        Q: list of lists of floats, shape (seq_len, d_model). Queries, all
            heads side by side.
        K: list of lists of floats, shape (seq_len, d_model). Keys, all heads
            side by side.
        V: list of lists of floats, shape (seq_len, d_model). Values, all heads
            side by side.
        slopes: list of floats, shape (num_heads,). One distance-penalty slope
            per head.
        causal: bool. If True, token i attends only to j <= i.

    Returns:
        A single np.ndarray of floats: the attention output.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
