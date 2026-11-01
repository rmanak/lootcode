import numpy as np


def linearRegressionGD(X, y, lr, steps):
    X = np.asarray(X, dtype=float)          # (N, d)
    y = np.asarray(y, dtype=float)
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    history = []
    for _ in range(steps):
        r = X @ w + b - y                   # residuals
        history.append(float(np.mean(r * r)))
        gw = 2.0 * (X.T @ r) / n            # d/dw of mean((Xw + b - y)^2)
        gb = 2.0 * r.mean()
        w = w - lr * gw
        b = b - lr * gb
    return [w.tolist(), float(b), history]
