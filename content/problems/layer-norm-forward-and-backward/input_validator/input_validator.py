"""Input-constraint validator for problem 'layer-norm-forward-and-backward'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: x and dy are both N x D with 1 <= N <= 64 and
1 <= D <= 64; gamma and beta have D entries; every entry of x is finite with
|x| <= 1000; every entry of gamma, beta and dy is finite with |v| <= 10; and
eps is a finite number with 1e-12 <= eps <= 1. The statement makes no promise
about the answer.
"""
import math

MAX_N, MAX_D = 64, 64


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def _matrix(a, rows, cols, bound):
    return (isinstance(a, list) and len(a) == rows
            and all(isinstance(r, list) and len(r) == cols and all(_num(v, bound) for v in r)
                    for r in a))


def _vector(a, n, bound):
    return isinstance(a, list) and len(a) == n and all(_num(v, bound) for v in a)


def validate_input(x, gamma, beta, dy, eps):
    if not isinstance(x, list) or not 1 <= len(x) <= MAX_N:
        return False
    if not isinstance(x[0], list) or not 1 <= len(x[0]) <= MAX_D:
        return False
    n, d = len(x), len(x[0])
    return (_matrix(x, n, d, 1000) and _matrix(dy, n, d, 10)
            and _vector(gamma, d, 10) and _vector(beta, d, 10)
            and _num(eps, 1) and eps >= 1e-12)
