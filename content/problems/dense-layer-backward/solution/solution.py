import numpy as np


def denseBackward(X, W, b, dY, activation):
    X = np.asarray(X, dtype=float)          # (N, Din)
    W = np.asarray(W, dtype=float)          # (Din, Dout)
    dY = np.asarray(dY, dtype=float)        # (N, Dout), gradient of the loss w.r.t. Y
    Z = X @ W + np.asarray(b, dtype=float)  # pre-activation
    if activation == "linear":
        dZ = dY
    elif activation == "relu":
        dZ = dY * (Z > 0)                   # relu'(0) = 0
    elif activation == "tanh":
        t = np.tanh(Z)
        dZ = dY * (1.0 - t * t)
    else:                                   # "sigmoid"
        s = 0.5 * (1.0 + np.tanh(0.5 * Z))  # = 1 / (1 + e^-Z), without overflow
        dZ = dY * s * (1.0 - s)
    return [(dZ @ W.T).tolist(), (X.T @ dZ).tolist(), dZ.sum(axis=0).tolist()]
