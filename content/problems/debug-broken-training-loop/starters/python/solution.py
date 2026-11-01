import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


# This loop runs, but it has seven bugs. Fix them so that it does exactly what
# the problem statement describes.
def trainLogistic(X, y, epochs, batchSize, lr, lrDecay, l2, permutations):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    losses = []
    for epoch in range(epochs):
        step = lr * lrDecay ** (epoch + 1)
        order = permutations[epoch]
        gw = np.zeros(d)
        for start in range(0, n, batchSize):
            idx = order[start:start + batchSize]
            xb = X[idx]
            yb = y[start:start + batchSize]
            err = sigmoid(xb @ w + b) - yb
            gw += xb.T @ err / batchSize + l2 * w
            gb = err.sum() / batchSize + l2 * b
            w = w - step * gw
            b = b - step * gb
        p = sigmoid(X @ w + b)
        losses.append(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))
    return [w.tolist(), float(b), losses]
