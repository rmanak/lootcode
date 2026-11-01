import numpy as np


def kMeans(points, initialCentroids, maxIters):
    X = np.asarray(points, dtype=float)              # (N, d)
    C = np.array(initialCentroids, dtype=float)      # (K, d), a copy we update
    labels = None
    for _ in range(maxIters):
        # squared distance from every point to every centroid: (N, K)
        d2 = ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
        new_labels = d2.argmin(axis=1)               # first minimum = lowest index
        if labels is not None and np.array_equal(new_labels, labels):
            break                                    # converged: nothing changed
        labels = new_labels
        for k in range(len(C)):
            members = X[labels == k]
            if len(members):                         # an empty cluster stays put
                C[k] = members.mean(axis=0)
    return C.tolist(), labels.tolist()
