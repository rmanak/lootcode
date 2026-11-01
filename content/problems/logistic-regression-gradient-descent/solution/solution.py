import numpy as np


def logisticRegressionGD(X, y, lr, steps):
    X = np.asarray(X, dtype=float)          # (N, d)
    y = np.asarray(y, dtype=float)          # (N,)
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    history = []
    for _ in range(steps):
        z = X @ w + b
        # Example i costs log(1 + exp(-m)), where m = z for a positive and -z
        # for a negative. logaddexp(0, -m) computes that without overflow, and
        # without the log(0) of the textbook y·log(p) + (1-y)·log(1-p) form.
        m = np.where(y == 1, z, -z)
        history.append(float(np.mean(np.logaddexp(0.0, -m))))
        p = np.exp(-np.logaddexp(0.0, -z))  # sigmoid(z), overflow-free
        r = p - y                           # dL/dz for each example, times N
        w = w - lr * (X.T @ r) / n
        b = b - lr * r.mean()
    return [w.tolist(), float(b), history]
