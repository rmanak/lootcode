import numpy as np

TIE = 1e-9   # gains closer than this count as equal (see the statement)


def bestSplit(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    n, d = X.shape
    classes = int(y.max()) + 1
    onehot = np.eye(classes)[y]

    def gini(counts, size):
        return 1.0 - ((counts / size) ** 2).sum(axis=-1)

    parent = gini(onehot.sum(axis=0), n)
    best = None                                       # (gain, feature, threshold)
    for j in range(d):
        order = np.argsort(X[:, j], kind="stable")
        xs = X[order, j]
        left = np.cumsum(onehot[order], axis=0)[:-1]  # class counts of the first i+1 points
        sizes = np.arange(1, n)
        cut = xs[1:] != xs[:-1]                       # only between distinct values
        if not cut.any():
            continue
        nl, cl = sizes[cut], left[cut]
        cr, nr = left[-1] + onehot[order][-1] - cl, n - nl
        gain = parent - (nl / n) * gini(cl, nl[:, None]) - (nr / n) * gini(cr, nr[:, None])
        thr = (xs[:-1][cut] + xs[1:][cut]) / 2        # midpoints, ascending
        i = int(np.argmax(gain >= gain.max() - TIE))  # lowest threshold among the tied best
        if best is None or gain[i] > best[0] + TIE:   # a later feature must win outright
            best = (float(gain[i]), j, float(thr[i]))
    return [best[1], best[2], best[0]]
