import numpy as np


def trainRanker(preferences, lr, steps):
    pairs = np.asarray(preferences, dtype=float)    # (N, 2, d)
    diff = pairs[:, 0, :] - pairs[:, 1, :]          # fixed for the whole run
    n, d = diff.shape
    w = np.zeros(d)
    for _ in range(steps):
        margins = diff @ w
        pull = 0.5 * (1.0 - np.tanh(0.5 * margins))  # sigmoid(-m), overflow-free
        grad = -(pull @ diff) / n
        w -= lr * grad
    return w.tolist()
