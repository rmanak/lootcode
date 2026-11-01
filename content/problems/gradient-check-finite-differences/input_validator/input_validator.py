"""Input-constraint validator for problem 'gradient-check-finite-differences'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X has 1 <= N <= 200 rows of the same length d with
1 <= d <= 10, every entry finite with |x| <= 10; y has N labels, each the int 1
or -1; w and analyticGrad have d finite entries with |v| <= 10 and |g| <= 1000;
lam finite in [0, 10]; h finite in [1e-5, 1e-2]. It also enforces the
statement's promise that the true gradient has norm at least 0.1 (so the
relative error is not dominated by rounding noise). numpy computes the true
gradient.
"""
import math

import numpy as np


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(X, y, w, lam, analyticGrad, h):
    if not isinstance(X, list) or not 1 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d or not all(_num(v, 10) for v in row):
            return False
    if not isinstance(y, list) or len(y) != len(X):
        return False
    if not all(isinstance(v, int) and not isinstance(v, bool) and v in (1, -1) for v in y):
        return False
    if not (isinstance(w, list) and len(w) == d and all(_num(v, 10) for v in w)):
        return False
    if not (isinstance(analyticGrad, list) and len(analyticGrad) == d and all(_num(v, 1000) for v in analyticGrad)):
        return False
    if not (_num(lam, 10) and lam >= 0 and _num(h, 1) and 1e-5 <= h <= 1e-2):
        return False
    A = np.asarray(X, dtype=float); Y = np.asarray(y, dtype=float); W = np.asarray(w, dtype=float)
    z = -Y * (A @ W)
    sig = np.exp(-np.logaddexp(0.0, -z))                     # sigmoid(z), stable
    grad = (-(Y * sig)[:, None] * A).mean(axis=0) + lam * W
    return float(np.linalg.norm(grad)) >= 0.1
