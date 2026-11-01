"""Input-constraint validator for problem 'info-nce-contrastive-loss'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: U and V are both N x d with 1 <= N <= 64 and
1 <= d <= 32; every entry finite (not a bool) with |v| <= 10; every row has
Euclidean norm >= 0.1; temperature finite in [0.001, 10].
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def _emb(M, n=None, d=None):
    if not isinstance(M, list) or not M or (n is not None and len(M) != n) or not isinstance(M[0], list):
        return None
    c = len(M[0]) if d is None else d
    for r in M:
        if not isinstance(r, list) or len(r) != c or not all(_num(v, -10, 10) for v in r):
            return None
        if math.sqrt(math.fsum(v * v for v in r)) < 0.1:
            return None
    return len(M), c


def validate_input(U, V, temperature):
    su = _emb(U)
    if su is None or not (1 <= su[0] <= 64 and 1 <= su[1] <= 32):
        return False
    if _emb(V, *su) is None:
        return False
    return _num(temperature, 0.001, 10)
