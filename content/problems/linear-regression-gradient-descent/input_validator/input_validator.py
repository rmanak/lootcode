"""Input-constraint validator for problem 'linear-regression-gradient-descent'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 rows of the same length d with
1 <= d <= 10, every feature finite with |x| <= 100; N finite targets with
|y| <= 1000; lr a finite number with 0 < lr <= 1; steps an int with
1 <= steps <= 1000. It also enforces the statement's promise that gradient
descent is stable: lr * lambda_max < 1.9, where lambda_max is the largest
eigenvalue of (2/N) * Zᵀ Z and Z is X with a column of ones appended (numpy is
used for the eigenvalue).
"""
import math

import numpy as np


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(X, y, lr, steps):
    if not isinstance(X, list) or not 1 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d or not all(_num(v, 100) for v in row):
            return False
    if not isinstance(y, list) or len(y) != len(X) or not all(_num(v, 1000) for v in y):
        return False
    if not (_num(lr, 1) and lr > 0):
        return False
    if not (isinstance(steps, int) and not isinstance(steps, bool) and 1 <= steps <= 1000):
        return False
    Z = np.hstack([np.asarray(X, dtype=float), np.ones((len(X), 1))])
    lam = float(np.linalg.eigvalsh(2.0 * Z.T @ Z / len(X))[-1])
    return lr * lam < 1.9
