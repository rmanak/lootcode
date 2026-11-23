import numpy as np


def groupedQueryAttention(X, Wq, Wk, Wv, Wo, numHeads, numKvHeads):
    """Causal self-attention with grouped-query attention (shared KV heads).

    Args:
        X: list of lists of floats, shape (seq_len, d_model). Token embeddings.
        Wq: list of lists of floats, shape (d_model, d_model). Query
            projection.
        Wk: list of lists of floats, shape (d_model, numKvHeads * head_dim).
            Key projection, head_dim = d_model / numHeads.
        Wv: list of lists of floats, shape (d_model, numKvHeads * head_dim).
            Value projection.
        Wo: list of lists of floats, shape (d_model, d_model). Output
            projection.
        numHeads: int. Number of query heads.
        numKvHeads: int. Number of key/value heads.

    Returns:
        A single np.ndarray of floats: the attention output.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
