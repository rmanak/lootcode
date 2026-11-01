import numpy as np


def scaledDotProductAttention(Q, K, V, mask):
    Q = np.asarray(Q, dtype=float)          # (n, dk)
    K = np.asarray(K, dtype=float)          # (m, dk)
    V = np.asarray(V, dtype=float)          # (m, dv)
    allowed = np.asarray(mask, dtype=int) == 1
    scores = Q @ K.T / np.sqrt(Q.shape[1])
    # A blocked key gets score -inf, so exp gives it weight exactly 0.
    scores = np.where(allowed, scores, -np.inf)
    # Subtract each row's largest ALLOWED score (every row has one), so every
    # exponent is <= 0 and the largest is exactly 0: no overflow, and the row
    # sum is at least 1.
    scores = scores - scores.max(axis=1, keepdims=True)
    e = np.exp(scores)
    weights = e / e.sum(axis=1, keepdims=True)
    return [(weights @ V).tolist(), weights.tolist()]
