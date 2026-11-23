import torch


def applyRope(x, positions, base, style):
    """Apply rotary position embeddings (RoPE) to a sequence of vectors.

    Args:
        x: float64 tensor, shape (seq_len, head_dim). One vector per token;
            head_dim is even.
        positions: int64 tensor, shape (seq_len,). Position of each token.
        base: float. Frequency base.
        style: str. "interleaved" or "half".

    Returns:
        A single float64 tensor: the input with every row rotated.
    """
    pass
