import numpy as np


def _dist(P, normal, offset):
    return np.abs(P @ normal + offset) / np.linalg.norm(normal)


def fitPlane(points, plane, triples, threshold):
    P = np.asarray(points, float)
    a, b, c, d = plane
    distances = _dist(P, np.array([a, b, c], float), d)

    best = None
    for t in triples:
        p0, p1, p2 = P[t[0]], P[t[1]], P[t[2]]
        normal = np.cross(p1 - p0, p2 - p0)
        inliers = _dist(P, normal, -normal @ p0) <= threshold
        count = int(inliers.sum())
        if best is None or count > best[0]:          # strict: the earliest triple wins a tie
            best = (count, inliers)

    Q = P[best[1]]
    mu = Q.mean(axis=0)
    normal = np.linalg.svd(Q - mu)[2][-1]            # smallest singular value's right vector
    refit = _dist(P, normal, -normal @ mu)
    outliers = np.flatnonzero(refit > threshold)
    return [distances, outliers.tolist(), refit]
