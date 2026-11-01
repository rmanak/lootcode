import numpy as np


def sigmoid(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))       # = 1 / (1 + e^-z), no overflow


def trainLogistic(X, y, epochs, batchSize, lr, lrDecay, l2, permutations):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    losses = []
    for epoch in range(epochs):
        step = lr * lrDecay ** epoch            # fix 1: the first epoch uses lr itself
        order = permutations[epoch]
        for start in range(0, n, batchSize):
            idx = order[start:start + batchSize]
            xb = X[idx]
            yb = y[idx]                         # fix 3: labels follow the same permutation
            err = sigmoid(xb @ w + b) - yb
            gw = xb.T @ err / len(idx) + l2 * w  # fix 2: fresh gradient per batch; fix 4: real batch size
            gb = err.sum() / len(idx)           # fix 5: no L2 on the bias
            w = w - step * gw
            b = b - step * gb
        z = X @ w + b
        bce = np.mean(np.logaddexp(0.0, z) - y * z)   # fix 6: log-loss without log(0)
        losses.append(bce + 0.5 * l2 * (w @ w))       # fix 7: the objective includes the L2 term
    return [w.tolist(), float(b), losses]
