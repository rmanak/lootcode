import numpy as np


def distanceDecayAttention(Q, K, V, slopes, causal):
    Q = np.asarray(Q, float)
    K = np.asarray(K, float)
    V = np.asarray(V, float)
    n, D = Q.shape
    H = len(slopes)
    dh = D // H
    idx = np.arange(n)
    dist = np.abs(idx[:, None] - idx[None, :])
    out = np.empty_like(V)
    for h in range(H):
        cols = slice(h * dh, (h + 1) * dh)
        S = Q[:, cols] @ K[:, cols].T / np.sqrt(dh) - slopes[h] * dist
        if causal:
            S = np.where(idx[None, :] <= idx[:, None], S, -np.inf)
        S = S - S.max(axis=1, keepdims=True)
        A = np.exp(S)
        A /= A.sum(axis=1, keepdims=True)
        out[:, cols] = A @ V[:, cols]
    return out
