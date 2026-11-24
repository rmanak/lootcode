import torch


def multiHeadSelfAttention(X, Wq, Wk, Wv, Wo, numHeads):
    """Multi-head causal self-attention (single sequence, no biases).

    Args:
        X: float32 tensor, shape (seq_len, d_model). Token embeddings.
        Wq: float32 tensor, shape (d_model, d_model). Query projection.
        Wk: float32 tensor, shape (d_model, d_model). Key projection.
        Wv: float32 tensor, shape (d_model, d_model). Value projection.
        Wo: float32 tensor, shape (d_model, d_model). Output projection.
        numHeads: int. Number of heads; divides d_model.

    Returns:
        A single float32 tensor: the attention output.
    """
    pass
