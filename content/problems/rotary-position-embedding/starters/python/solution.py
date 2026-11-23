import numpy as np


def applyRope(x, positions, base, style):
    """Apply rotary position embeddings (RoPE) to a sequence of vectors.

    Args:
        x: list of lists of floats, shape (seq_len, head_dim). One vector per
            token; head_dim is even.
        positions: list of ints, shape (seq_len,). Position of each token.
        base: float. Frequency base.
        style: str. "interleaved" or "half".

    Returns:
        A single np.ndarray of floats: the input with every row rotated.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
