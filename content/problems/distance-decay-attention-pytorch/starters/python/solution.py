import torch


def distanceDecayAttention(Q, K, V, slopes, causal):
    """Multi-head self-attention with a per-head linear distance (ALiBi) bias.

    Args:
        Q: float32 tensor, shape (seq_len, d_model). Queries, all heads side by
            side.
        K: float32 tensor, shape (seq_len, d_model). Keys, all heads side by
            side.
        V: float32 tensor, shape (seq_len, d_model). Values, all heads side by
            side.
        slopes: float32 tensor, shape (num_heads,). One distance-penalty slope
            per head.
        causal: bool. If True, token i attends only to j <= i.

    Returns:
        A single float32 tensor: the attention output.
    """
    pass
