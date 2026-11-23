import torch


def multiHeadSelfAttention(X, Wq, Wk, Wv, Wo, numHeads):
    """Multi-head causal self-attention (single sequence, no biases).

    Args:
        X: float64 tensor, shape (seq_len, d_model). Token embeddings.
        Wq: float64 tensor, shape (d_model, d_model). Query projection.
        Wk: float64 tensor, shape (d_model, d_model). Key projection.
        Wv: float64 tensor, shape (d_model, d_model). Value projection.
        Wo: float64 tensor, shape (d_model, d_model). Output projection.
        numHeads: int. Number of heads; divides d_model.

    Returns:
        A single float64 tensor: the attention output.
    """
    pass
