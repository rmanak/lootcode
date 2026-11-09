import numpy as np


def kMedians(points, initialCenters, maxIters):
    P = np.asarray(points, float)
    C = np.asarray(initialCenters, float).copy()
    labels = None
    for _ in range(maxIters):
        dist = np.abs(P[:, None, :] - C[None, :, :]).sum(axis=2)    # (N, K)
        new = dist.argmin(axis=1)                                    # first minimum = lowest index
        if labels is not None and np.array_equal(new, labels):
            break
        labels = new
        for k in range(len(C)):
            members = P[labels == k]
            if len(members):
                C[k] = np.median(members, axis=0)
    cost = float(np.abs(P - C[labels]).sum())
    return [C.tolist(), labels.tolist(), cost]
