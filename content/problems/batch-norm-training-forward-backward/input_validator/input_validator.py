"""Input-constraint validator for problem 'batch-norm-training-forward-backward'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: x and dy are N x D with 2 <= N <= 256 and
1 <= D <= 64; |x| <= 10^4 and |dy| <= 10; gamma, beta, runningMean, runningVar
have D entries with |gamma|, |beta| <= 10, |runningMean| <= 10^4 and
0 <= runningVar <= 10^8; eps finite in [1e-8, 0.1]; momentum finite in [0, 1].
All numbers finite and not bools.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def _vec(v, d, lo, hi):
    return isinstance(v, list) and len(v) == d and all(_num(t, lo, hi) for t in v)


def validate_input(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    if not isinstance(x, list) or not 2 <= len(x) <= 256 or not isinstance(x[0], list):
        return False
    d = len(x[0])
    if not 1 <= d <= 64:
        return False
    if not all(_vec(r, d, -1e4, 1e4) for r in x):
        return False
    if not (isinstance(dy, list) and len(dy) == len(x) and all(_vec(r, d, -10, 10) for r in dy)):
        return False
    if not (_vec(gamma, d, -10, 10) and _vec(beta, d, -10, 10)):
        return False
    if not (_vec(runningMean, d, -1e4, 1e4) and _vec(runningVar, d, 0, 1e8)):
        return False
    return _num(eps, 1e-8, 0.1) and _num(momentum, 0, 1)
