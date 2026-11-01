"""Input-constraint validator for problem 'linear-svm-pegasos'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 rows of the same length d with
1 <= d <= 10, every feature finite with |x| <= 100; N labels each exactly
1 or -1 (ints); lam finite with 1e-4 <= lam <= 10; order a list of 1..2000
ints, each a valid row index in [0, N).

Not checked here (it needs the whole trajectory): the statement's promise that
no margin lands within 1e-6 of 1 unless it is exactly 1 at a step where every
float formula computes it exactly. The case generator vets that with an exact
Fraction replay.
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(X, y, lam, order):
    if not isinstance(X, list) or not 1 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d or not all(_num(v, 100) for v in row):
            return False
    if not isinstance(y, list) or len(y) != len(X) or not all(_int(v) and v in (1, -1) for v in y):
        return False
    if not (_num(lam, 10) and lam >= 1e-4):
        return False
    return (isinstance(order, list) and 1 <= len(order) <= 2000
            and all(_int(i) and 0 <= i < len(X) for i in order))
