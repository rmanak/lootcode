"""Input-constraint validator for problem 'ridge-regression-closed-form'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 2 <= N <= 200 rows of the same length d with
1 <= d <= 10, every feature finite with |x| <= 100; N finite targets with
|y| <= 1000; lam a finite number with 0 <= lam <= 10^4. It also enforces the
statement's promise that the answer is unique and well conditioned: with Xc
the column-centered X, the matrix Xcᵀ·Xc + lam·I has condition number at most
10^6 (so with lam = 0 the columns of [X, 1] are linearly independent). numpy
computes the condition number.
"""
import math

import numpy as np


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(X, y, lam):
    if not isinstance(X, list) or not 2 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d or not all(_num(v, 100) for v in row):
            return False
    if not isinstance(y, list) or len(y) != len(X) or not all(_num(v, 1000) for v in y):
        return False
    if not (_num(lam, 10_000) and lam >= 0):
        return False
    A = np.asarray(X, dtype=float)
    Ac = A - A.mean(axis=0)
    M = Ac.T @ Ac + lam * np.eye(d)
    s = np.linalg.svd(M, compute_uv=False)
    return s[-1] > 0 and s[0] / s[-1] <= 1e6
