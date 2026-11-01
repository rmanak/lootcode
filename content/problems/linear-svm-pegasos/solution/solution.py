import numpy as np


def pegasos(X, y, lam, order):
    X = np.asarray(X, dtype=float)              # (N, d)
    w = np.zeros(X.shape[1])
    for t, i in enumerate(order, start=1):
        eta = 1.0 / (lam * t)
        margin = y[i] * (w @ X[i])              # uses w from before this step
        w = (1.0 - eta * lam) * w               # the regularizer always shrinks w
        if margin < 1:                          # strictly inside the margin
            w = w + eta * y[i] * X[i]
    return w.tolist()
