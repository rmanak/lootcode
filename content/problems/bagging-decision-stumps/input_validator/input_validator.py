"""Input-constraint validator for problem 'bagging-decision-stumps'.

Hand-written. X is n x d (1 <= n <= 200, 1 <= d <= 8) and XTest m x d
(1 <= m <= 200), every value finite (not a bool) with |v| <= 1e4; y has n
integer labels with |label| <= 1000; 1 to 30 bootstraps, each a list of 1..n
int indices in [0, n).
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 1e4


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _mat(A, d=None):
    if not isinstance(A, list) or not 1 <= len(A) <= 200 or not isinstance(A[0], list):
        return None
    d = len(A[0]) if d is None else d
    if not 1 <= d <= 8:
        return None
    if not all(isinstance(r, list) and len(r) == d and all(_num(v) for v in r) for r in A):
        return None
    return d


def validate_input(X, y, bootstraps, XTest):
    d = _mat(X)
    if d is None or _mat(XTest, d) is None:
        return False
    n = len(X)
    if not isinstance(y, list) or len(y) != n or not all(_int(v) and abs(v) <= 1000 for v in y):
        return False
    if not isinstance(bootstraps, list) or not 1 <= len(bootstraps) <= 30:
        return False
    for b in bootstraps:
        if not isinstance(b, list) or not 1 <= len(b) <= n:
            return False
        if not all(_int(i) and 0 <= i < n for i in b):
            return False
    return True
