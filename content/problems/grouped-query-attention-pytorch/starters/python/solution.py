import torch


def groupedQueryAttention(X, Wq, Wk, Wv, Wo, numHeads, numKvHeads):
    """X: (T, D) float64 tensor; Wq, Wo: (D, D); Wk, Wv: (D, numKvHeads * dh)
    float64 tensors; numHeads, numKvHeads: int. Return a (T, D) float64 tensor."""
    pass
