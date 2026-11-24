import torch


def attentionBackward(Q, K, V, dO, causal):
    """Forward and backward pass of single-head scaled dot-product attention.

    Args:
        Q: float32 tensor, shape (num_queries, head_dim). Queries.
        K: float32 tensor, shape (num_keys, head_dim). Keys.
        V: float32 tensor, shape (num_keys, value_dim). Values.
        dO: float32 tensor, shape (num_queries, value_dim). Upstream gradient
            dLoss/dO.
        causal: bool. If True, apply a causal mask; num_queries == num_keys
            then.

    Returns:
        A list [O, dQ, dK, dV] (a tuple works too):
            O: float32 tensor. Attention output.
            dQ: float32 tensor. Gradient w.r.t. Q.
            dK: float32 tensor. Gradient w.r.t. K.
            dV: float32 tensor. Gradient w.r.t. V.
    """
    pass
