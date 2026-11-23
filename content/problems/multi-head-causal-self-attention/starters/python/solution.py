import numpy as np


def multiHeadSelfAttention(X, Wq, Wk, Wv, Wo, numHeads):
    """Multi-head causal self-attention (single sequence, no biases).

    Args:
        X: list of lists of floats, shape (seq_len, d_model). Token embeddings.
        Wq: list of lists of floats, shape (d_model, d_model). Query
            projection.
        Wk: list of lists of floats, shape (d_model, d_model). Key projection.
        Wv: list of lists of floats, shape (d_model, d_model). Value
            projection.
        Wo: list of lists of floats, shape (d_model, d_model). Output
            projection.
        numHeads: int. Number of heads; divides d_model.

    Returns:
        A single np.ndarray of floats: the attention output.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
