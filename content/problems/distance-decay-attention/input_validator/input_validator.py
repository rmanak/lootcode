"""Input-constraint validator for problem 'distance-decay-attention'.

Hand-written. Q, K, V are each n x D (1 <= n, D <= 64), every entry finite
(not a bool) with |v| <= 30; slopes has 1..8 numbers in [0, 50] and its
length divides D; causal is a bool.
"""
import math


def _num(v, lim):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= lim


def _mat(A, n=None, D=None):
    if not isinstance(A, list) or not A or not isinstance(A[0], list):
        return None
    r, c = len(A), len(A[0])
    if (n is not None and r != n) or (D is not None and c != D) or not 1 <= r <= 64 or not 1 <= c <= 64:
        return None
    if not all(isinstance(row, list) and len(row) == c and all(_num(v, 30) for v in row) for row in A):
        return None
    return r, c


def validate_input(Q, K, V, slopes, causal):
    s = _mat(Q)
    if s is None or _mat(K, *s) != s or _mat(V, *s) != s:
        return False
    if not isinstance(slopes, list) or not 1 <= len(slopes) <= 8 or s[1] % len(slopes):
        return False
    if not all(_num(a, 50) and a >= 0 for a in slopes):
        return False
    return isinstance(causal, bool)
