"""Input-constraint validator for problem 'attention-backward-pass'.

Hand-written. Q n x d, K m x d, V m x dv, dO n x dv with 1 <= n, m <= 64 and
1 <= d, dv <= 32; every entry finite (not a bool) with |v| <= 30; causal a
bool, and n == m when it is true.
"""
import math


def _mat(A, rows=None, cols=None, rmax=64, cmax=32):
    if not isinstance(A, list) or not A or not isinstance(A[0], list):
        return None
    r, c = len(A), len(A[0])
    if (rows is not None and r != rows) or (cols is not None and c != cols):
        return None
    if not 1 <= r <= rmax or not 1 <= c <= cmax:
        return None
    for row in A:
        if not isinstance(row, list) or len(row) != c:
            return None
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 30 for v in row):
            return None
    return r, c


def validate_input(Q, K, V, dO, causal):
    q = _mat(Q)
    if q is None:
        return False
    n, d = q
    k = _mat(K, cols=d)
    if k is None:
        return False
    m = k[0]
    v = _mat(V, rows=m)
    if v is None or _mat(dO, rows=n, cols=v[1]) is None:
        return False
    if not isinstance(causal, bool):
        return False
    return not causal or n == m
