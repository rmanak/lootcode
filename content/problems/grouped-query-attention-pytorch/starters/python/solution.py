import torch


def groupedQueryAttention(X, Wq, Wk, Wv, Wo, numHeads, numKvHeads):
    """Causal self-attention with grouped-query attention (shared KV heads).

    Args:
        X: float32 tensor, shape (seq_len, d_model). Token embeddings.
        Wq: float32 tensor, shape (d_model, d_model). Query projection.
        Wk: float32 tensor, shape (d_model, numKvHeads * head_dim). Key
            projection, head_dim = d_model / numHeads.
        Wv: float32 tensor, shape (d_model, numKvHeads * head_dim). Value
            projection.
        Wo: float32 tensor, shape (d_model, d_model). Output projection.
        numHeads: int. Number of query heads.
        numKvHeads: int. Number of key/value heads.

    Returns:
        A single float32 tensor: the attention output.
    """
    pass
