from collections import Counter


def _majority(labels):
    """Most common label; ties to the smaller label."""
    counts = Counter(labels)
    top = max(counts.values())
    return min(l for l, c in counts.items() if c == top)


def _fit_stump(rows, labels):
    best = None                                    # (errors, j, t, left, right)
    d = len(rows[0])
    for j in range(d):
        order = sorted(range(len(rows)), key=lambda i: rows[i][j])
        left, right = Counter(), Counter(labels)
        k = 0
        while k < len(order):
            v = rows[order[k]][j]
            while k < len(order) and rows[order[k]][j] == v:   # move every row with value v left
                lab = labels[order[k]]
                left[lab] += 1
                right[lab] -= 1
                k += 1
            if k == len(order):
                break                                          # no right neighbour: not a threshold
            t = (v + rows[order[k]][j]) / 2
            lmaj = _majority(+left)
            rmaj = _majority(+right)
            err = (sum(left.values()) - left[lmaj]) + (sum(right.values()) - right[rmaj])
            if best is None or err < best[0]:                  # strict: keeps smallest j, then t
                best = (err, j, t, lmaj, rmaj)
    if best is None:
        lab = _majority(labels)
        return [-1, 0.0, lab, lab]
    return list(best[1:])


def baggingStumps(X, y, bootstraps, XTest):
    stumps = [_fit_stump([X[i] for i in idx], [y[i] for i in idx]) for idx in bootstraps]
    preds = []
    for x in XTest:
        votes = [l if j < 0 or x[j] <= t else r for j, t, l, r in stumps]
        preds.append(_majority(votes))
    return [stumps, preds]
