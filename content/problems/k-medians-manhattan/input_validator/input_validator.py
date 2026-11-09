"""Input-constraint validator for problem 'k-medians-manhattan'.

Hand-written. points is N x d ints (1 <= N <= 2000, 1 <= d <= 4,
|coord| <= 1e4); initialCenters is K x d (1 <= K <= 20) numbers that are
multiples of 0.5 with |v| <= 1e4; maxIters an int in [1, 100].
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(points, initialCenters, maxIters):
    if not isinstance(points, list) or not 1 <= len(points) <= 2000 or not isinstance(points[0], list):
        return False
    d = len(points[0])
    if not 1 <= d <= 4:
        return False
    if not all(isinstance(p, list) and len(p) == d and all(_int(v) and abs(v) <= 10**4 for v in p) for p in points):
        return False
    C = initialCenters
    if not isinstance(C, list) or not 1 <= len(C) <= 20:
        return False
    for c in C:
        if not isinstance(c, list) or len(c) != d:
            return False
        for v in c:
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
                return False
            if abs(v) > 10**4 or (2 * v) != int(2 * v):
                return False
    return _int(maxIters) and 1 <= maxIters <= 100
