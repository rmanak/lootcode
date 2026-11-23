import torch


def attentionBackward(Q, K, V, dO, causal):
    """Forward and backward pass of single-head scaled dot-product attention.

    Args:
        Q: float64 tensor, shape (num_queries, head_dim). Queries.
        K: float64 tensor, shape (num_keys, head_dim). Keys.
        V: float64 tensor, shape (num_keys, value_dim). Values.
        dO: float64 tensor, shape (num_queries, value_dim). Upstream gradient
            dLoss/dO.
        causal: bool. If True, apply a causal mask; num_queries == num_keys
            then.

    Returns:
        A list [O, dQ, dK, dV] (a tuple works too):
            O: float64 tensor. Attention output.
            dQ: float64 tensor. Gradient w.r.t. Q.
            dK: float64 tensor. Gradient w.r.t. K.
            dV: float64 tensor. Gradient w.r.t. V.
    """
    pass
