"""Input-constraint validator for problem 'matrix-prefix-products-backward'.

Hand-written. W and dP are both N x D x D (1 <= N <= 60, 1 <= D <= 6), every
entry finite (not a bool) with |v| <= 2. Also checks the statement's promise
that every prefix product and every gradient entry is below 1e6 in absolute
value (computed directly, O(N^2 D^3) at these sizes).
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 2


def _stack(A, N=None, D=None):
    if not isinstance(A, list) or not A:
        return None
    N = len(A) if N is None else N
    if len(A) != N or not 1 <= N <= 60:
        return None
    if not isinstance(A[0], list):
        return None
    D = len(A[0]) if D is None else D
    if not 1 <= D <= 6:
        return None
    for M in A:
        if not isinstance(M, list) or len(M) != D:
            return None
        for r in M:
            if not isinstance(r, list) or len(r) != D or not all(_num(v) for v in r):
                return None
    return N, D


def _mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def _t(A):
    return [list(r) for r in zip(*A)]


def validate_input(W, dP):
    s = _stack(W)
    if s is None or _stack(dP, *s) != s:
        return False
    N, D = s
    eye = [[1.0 if i == j else 0.0 for j in range(D)] for i in range(D)]
    P, acc = [], eye
    for M in W:
        acc = _mm(acc, M)
        P.append(acc)
    if any(abs(v) >= 1e6 for M in P for r in M for v in r):
        return False
    R = None
    for j in range(N - 1, -1, -1):
        R = dP[j] if R is None else [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(dP[j], _mm(R, _t(W[j + 1])))]
        g = _mm(_t(P[j - 1] if j else eye), R)
        if any(abs(v) >= 1e6 for r in g for v in r):
            return False
    return True
