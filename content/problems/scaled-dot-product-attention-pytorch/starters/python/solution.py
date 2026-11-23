import torch


def scaledDotProductAttention(Q, K, V, mask):
    """Masked scaled dot-product attention.

    Args:
        Q: float64 tensor, shape (num_queries, d_k). Queries.
        K: float64 tensor, shape (num_keys, d_k). Keys.
        V: float64 tensor, shape (num_keys, d_v). Values.
        mask: int64 tensor, shape (num_queries, num_keys). 1 = query i may
            attend to key j, 0 = it may not.

    Returns:
        A list [output, weights] (a tuple works too):
            output: float64 tensor. The attention output.
            weights: float64 tensor. The attention weights.
    """
    pass
