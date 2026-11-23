import torch


def distanceDecayAttention(Q, K, V, slopes, causal):
    """Multi-head self-attention with a per-head linear distance (ALiBi) bias.

    Args:
        Q: float64 tensor, shape (seq_len, d_model). Queries, all heads side by
            side.
        K: float64 tensor, shape (seq_len, d_model). Keys, all heads side by
            side.
        V: float64 tensor, shape (seq_len, d_model). Values, all heads side by
            side.
        slopes: float64 tensor, shape (num_heads,). One distance-penalty slope
            per head.
        causal: bool. If True, token i attends only to j <= i.

    Returns:
        A single float64 tensor: the attention output.
    """
    pass
