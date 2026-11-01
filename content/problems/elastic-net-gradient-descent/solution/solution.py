import numpy as np


def elasticNetGD(X, y, alpha, l1Ratio, lr, steps):
    X = np.asarray(X, dtype=float)              # (N, d)
    y = np.asarray(y, dtype=float)
    n, d = X.shape
    l1 = alpha * l1Ratio                        # weight of sum |w_j|
    l2 = alpha * (1.0 - l1Ratio)                # weight of (1/2) sum w_j^2
    w = np.zeros(d)
    b = 0.0
    history = []
    for _ in range(steps):
        r = X @ w + b - y
        history.append(float(r @ r / (2 * n) + l1 * np.abs(w).sum() + 0.5 * l2 * (w @ w)))
        gw = X.T @ r / n + l1 * np.sign(w) + l2 * w     # np.sign(0) == 0
        gb = r.mean()
        w = w - lr * gw
        b = b - lr * gb
    return [w.tolist(), float(b), history]
