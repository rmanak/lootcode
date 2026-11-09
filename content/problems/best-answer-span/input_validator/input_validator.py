"""Input-constraint validator for problem 'best-answer-span'.

Hand-written. startLogits and endLogits are both B x T (1 <= B <= 64,
1 <= T <= 512), every value a multiple of 0.125 (not a bool) with
|v| <= 100; goldStarts/goldEnds B ints with 0 <= start <= end < T;
maxLen an int in [1, T].
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _mat(A, B=None, T=None):
    if not isinstance(A, list) or not A or not isinstance(A[0], list):
        return None
    b, t = len(A), len(A[0])
    if (B is not None and b != B) or (T is not None and t != T) or not 1 <= b <= 64 or not 1 <= t <= 512:
        return None
    for r in A:
        if not isinstance(r, list) or len(r) != t:
            return None
        for v in r:
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) or abs(v) > 100:
                return None
            if v * 8 != int(v * 8):
                return None
    return b, t


def validate_input(startLogits, endLogits, goldStarts, goldEnds, maxLen):
    s = _mat(startLogits)
    if s is None or _mat(endLogits, *s) != s:
        return False
    B, T = s
    for g in (goldStarts, goldEnds):
        if not isinstance(g, list) or len(g) != B or not all(_int(v) and 0 <= v < T for v in g):
            return False
    if any(a > b for a, b in zip(goldStarts, goldEnds)):
        return False
    return _int(maxLen) and 1 <= maxLen <= T
