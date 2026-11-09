"""Input-constraint validator for problem 'bernoulli-naive-bayes'.

Hand-written. X is n x d and XTest m x d with 1 <= n, m <= 1000 and
1 <= d <= 200, every entry the int 0 or 1; y has n integer labels with
|label| <= 1e6 and at most 20 distinct values; alpha a number in (0, 10].
"""
import math


def _mat(A, d=None):
    if not isinstance(A, list) or not 1 <= len(A) <= 1000 or not isinstance(A[0], list):
        return None
    d = len(A[0]) if d is None else d
    if not 1 <= d <= 200:
        return None
    for r in A:
        if not isinstance(r, list) or len(r) != d:
            return None
        if not all(isinstance(v, int) and not isinstance(v, bool) and v in (0, 1) for v in r):
            return None
    return d


def validate_input(X, y, XTest, alpha):
    d = _mat(X)
    if d is None or _mat(XTest, d) is None:
        return False
    if not isinstance(y, list) or len(y) != len(X):
        return False
    if not all(isinstance(v, int) and not isinstance(v, bool) and abs(v) <= 10**6 for v in y):
        return False
    if len(set(y)) > 20:
        return False
    return (isinstance(alpha, (int, float)) and not isinstance(alpha, bool)
            and math.isfinite(alpha) and 0 < alpha <= 10)
