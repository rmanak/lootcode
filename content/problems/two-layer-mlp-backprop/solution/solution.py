import numpy as np


def mlpBackprop(X, y, W1, b1, W2, b2):
    X = np.asarray(X, dtype=float)           # (N, D)
    W1 = np.asarray(W1, dtype=float)         # (D, H)
    W2 = np.asarray(W2, dtype=float)         # (H, C)
    b1 = np.asarray(b1, dtype=float)
    b2 = np.asarray(b2, dtype=float)
    n = len(X)
    rows, labels = np.arange(n), np.asarray(y, dtype=int)
    # forward
    a = X @ W1 + b1                          # pre-activations
    h = np.maximum(a, 0.0)                   # ReLU
    z = h @ W2 + b2                          # logits
    shifted = z - z.max(axis=1, keepdims=True)
    log_p = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
    loss = -log_p[rows, labels].mean()
    # backward
    dz = np.exp(log_p)
    dz[rows, labels] -= 1.0
    dz /= n                                  # d loss / d logits
    dW2 = h.T @ dz
    db2 = dz.sum(axis=0)
    dh = dz @ W2.T
    da = dh * (a > 0)                        # ReLU'(a) = 1 if a > 0, else 0 (also at 0)
    dW1 = X.T @ da
    db1 = da.sum(axis=0)
    return [float(loss), dW1.tolist(), db1.tolist(), dW2.tolist(), db2.tolist()]
