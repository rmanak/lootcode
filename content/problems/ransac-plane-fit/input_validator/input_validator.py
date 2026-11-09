"""Input-constraint validator for problem 'ransac-plane-fit'.

Hand-written. points: 4..2000 points of 3 finite coords with |v| <= 1000;
plane: 4 finite numbers with (a, b, c) != 0; triples: 1..200 lists of 3
distinct ints in [0, n); threshold a number in (0, 100]. Also checks the
statement's promises: no triple is (near-)collinear, every distance compared
with threshold (each triple's plane, and the refitted plane) is at least
1e-6 away from it, and the winning inliers are not collinear.
"""
import math

import numpy as np


def _num(v, lim):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= lim


def validate_input(points, plane, triples, threshold):
    if not isinstance(points, list) or not 4 <= len(points) <= 2000:
        return False
    if not all(isinstance(p, list) and len(p) == 3 and all(_num(v, 1000) for v in p) for p in points):
        return False
    if not isinstance(plane, list) or len(plane) != 4 or not all(_num(v, 1e300) for v in plane):
        return False
    if plane[0] == plane[1] == plane[2] == 0:
        return False
    if not _num(threshold, 100) or threshold <= 0:
        return False
    n = len(points)
    if not isinstance(triples, list) or not 1 <= len(triples) <= 200:
        return False
    for t in triples:
        if not isinstance(t, list) or len(t) != 3 or len(set(t)) != 3:
            return False
        if not all(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < n for i in t):
            return False
    P = np.asarray(points, float)
    best = None
    for t in triples:
        e1, e2 = P[t[1]] - P[t[0]], P[t[2]] - P[t[0]]
        nrm = np.cross(e1, e2)
        if np.linalg.norm(nrm) <= 1e-6 * max(1.0, np.linalg.norm(e1) * np.linalg.norm(e2)):
            return False
        dist = np.abs(P @ nrm - nrm @ P[t[0]]) / np.linalg.norm(nrm)
        if np.any(np.abs(dist - threshold) < 1e-6):
            return False
        inl = dist <= threshold
        if best is None or inl.sum() > best.sum():
            best = inl
    Q = P[best]
    if len(Q) < 3:
        return False
    s = np.linalg.svd(Q - Q.mean(0), compute_uv=False)
    if s[1] <= 1e-9 * max(1.0, s[0]):
        return False
    mu = Q.mean(0)
    nrm = np.linalg.svd(Q - mu)[2][-1]
    return not np.any(np.abs(np.abs((P - mu) @ nrm) - threshold) < 1e-6)
