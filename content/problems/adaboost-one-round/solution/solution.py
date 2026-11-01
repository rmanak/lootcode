import math

import numpy as np

TIE = 1e-9


def adaboostRound(X, y, weights):
    X = np.asarray(X, dtype=float)              # (N, d)
    y = np.asarray(y, dtype=float)
    w = np.asarray(weights, dtype=float)
    w = w / w.sum()                             # error is a fraction of the total weight
    best = None                                 # (error, feature, threshold, polarity)
    for j in range(X.shape[1]):
        order = np.argsort(X[:, j], kind="stable")
        xs, ys, ws = X[order, j], y[order], w[order]
        # Polarity +1 predicts +1 above the threshold and -1 at or below it, so
        # it misclassifies the +1s on the left and the -1s on the right.
        left_pos = np.cumsum(ws * (ys > 0))
        right_neg = (ws * (ys < 0)).sum() - np.cumsum(ws * (ys < 0))
        for i in range(len(xs) - 1):
            if xs[i] == xs[i + 1]:
                continue
            t = (xs[i] + xs[i + 1]) / 2
            err_pos = left_pos[i] + right_neg[i]
            for err, p in ((err_pos, 1), (1.0 - err_pos, -1)):
                if best is None or err < best[0] - TIE:
                    best = (err, j, t, p)
    err, j, t, p = best
    alpha = 0.5 * math.log((1 - err) / err)
    h = np.where(X[:, j] > t, p, -p)
    new = w * np.exp(-alpha * y * h)
    return [j, float(t), p, alpha, (new / new.sum()).tolist()]
