import numpy as np


def groupedQueryAttention(X, Wq, Wk, Wv, Wo, numHeads, numKvHeads):
    X = np.asarray(X, dtype=float)              # (T, D)
    T, D = X.shape
    dh = D // numHeads
    group = numHeads // numKvHeads              # query heads per key/value head
    Q = X @ np.asarray(Wq, dtype=float)         # (T, numHeads * dh)
    K = X @ np.asarray(Wk, dtype=float)         # (T, numKvHeads * dh)
    V = X @ np.asarray(Wv, dtype=float)
    causal = np.tril(np.ones((T, T), dtype=bool))
    heads = []
    for h in range(numHeads):
        g = h // group                          # consecutive query heads share one KV head
        q = Q[:, h * dh:(h + 1) * dh]
        k = K[:, g * dh:(g + 1) * dh]
        v = V[:, g * dh:(g + 1) * dh]
        s = np.where(causal, q @ k.T / np.sqrt(dh), -np.inf)
        s = s - s.max(axis=1, keepdims=True)    # exponents <= 0: no overflow
        w = np.exp(s)
        w /= w.sum(axis=1, keepdims=True)
        heads.append(w @ v)
    return (np.concatenate(heads, axis=1) @ np.asarray(Wo, dtype=float)).tolist()
