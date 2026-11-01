import numpy as np


def gradientCheck(X, y, w, lam, analyticGrad, h):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    a = np.asarray(analyticGrad, dtype=float)

    def loss(v):
        z = -y * (X @ v)
        # log(1 + exp(z)) without overflow: logaddexp(0, z).
        return np.logaddexp(0.0, z).mean() + 0.5 * lam * (v @ v)

    num = np.zeros_like(w)
    for j in range(len(w)):
        e = np.zeros_like(w)
        e[j] = h
        num[j] = (loss(w + e) - loss(w - e)) / (2 * h)       # central difference
    denom = np.linalg.norm(a) + np.linalg.norm(num)
    rel = np.linalg.norm(a - num) / denom if denom else 0.0
    return [num.tolist(), float(rel)]
