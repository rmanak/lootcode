"""Input-constraint validator for problem 'two-layer-mlp-backprop'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is N x D with 1 <= N <= 64 and 1 <= D <= 16;
W1 is D x H and b1 has H entries with 1 <= H <= 32; W2 is H x C and b2 has C
entries with 2 <= C <= 10; every entry of X, W1, b1, W2, b2 is a finite number
with |v| <= 100; y has N int labels with 0 <= label < C.
"""
import math


def _num(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= 100)


def _matrix(a, rows, cols):
    return (isinstance(a, list) and len(a) == rows
            and all(isinstance(r, list) and len(r) == cols and all(_num(v) for v in r) for r in a))


def _vector(a, n):
    return isinstance(a, list) and len(a) == n and all(_num(v) for v in a)


def validate_input(X, y, W1, b1, W2, b2):
    if not isinstance(X, list) or not 1 <= len(X) <= 64 or not isinstance(X[0], list):
        return False
    n, d = len(X), len(X[0])
    if not 1 <= d <= 16 or not _matrix(X, n, d):
        return False
    if not isinstance(W1, list) or len(W1) != d or not isinstance(W1[0], list):
        return False
    h = len(W1[0])
    if not 1 <= h <= 32 or not _matrix(W1, d, h) or not _vector(b1, h):
        return False
    if not isinstance(W2, list) or len(W2) != h or not isinstance(W2[0], list):
        return False
    c = len(W2[0])
    if not 2 <= c <= 10 or not _matrix(W2, h, c) or not _vector(b2, c):
        return False
    return (isinstance(y, list) and len(y) == n
            and all(isinstance(v, int) and not isinstance(v, bool) and 0 <= v < c for v in y))
