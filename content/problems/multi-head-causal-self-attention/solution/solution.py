import numpy as np


def multiHeadSelfAttention(X, Wq, Wk, Wv, Wo, numHeads):
    X = np.asarray(X, dtype=float)              # (T, D)
    T, D = X.shape
    dh = D // numHeads
    Q = X @ np.asarray(Wq, dtype=float)
    K = X @ np.asarray(Wk, dtype=float)
    V = X @ np.asarray(Wv, dtype=float)
    causal = np.tril(np.ones((T, T), dtype=bool))  # position i sees positions 0..i
    heads = []
    for h in range(numHeads):
        cols = slice(h * dh, (h + 1) * dh)       # head h owns one contiguous block
        s = Q[:, cols] @ K[:, cols].T / np.sqrt(dh)
        s = np.where(causal, s, -np.inf)
        # Subtract each row's largest visible score: exponents <= 0, no overflow.
        s = s - s.max(axis=1, keepdims=True)
        w = np.exp(s)
        w /= w.sum(axis=1, keepdims=True)
        heads.append(w @ V[:, cols])
    return (np.concatenate(heads, axis=1) @ np.asarray(Wo, dtype=float)).tolist()
