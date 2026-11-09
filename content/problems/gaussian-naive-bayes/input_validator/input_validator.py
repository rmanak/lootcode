"""Input-constraint validator for problem 'gaussian-naive-bayes'.

Hand-written. X is n x d and XTest m x d with 1 <= n, m <= 1000 and
1 <= d <= 50, every value finite (not a bool) with |v| <= 1e4; y has n integer
labels with |label| <= 1e6 and at most 20 distinct values.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 1e4


def _mat(A, rows_max, d=None):
    if not isinstance(A, list) or not 1 <= len(A) <= rows_max or not isinstance(A[0], list):
        return None
    d = len(A[0]) if d is None else d
    if not 1 <= d <= 50:
        return None
    if not all(isinstance(r, list) and len(r) == d and all(_num(v) for v in r) for r in A):
        return None
    return d


def validate_input(X, y, XTest):
    d = _mat(X, 1000)
    if d is None or _mat(XTest, 1000, d) is None:
        return False
    if not isinstance(y, list) or len(y) != len(X):
        return False
    if not all(isinstance(v, int) and not isinstance(v, bool) and abs(v) <= 10**6 for v in y):
        return False
    return len(set(y)) <= 20
