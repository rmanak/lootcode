"""Input-constraint validator for problem 'softmax-regression-gradient-descent'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 rows of the same length d with
1 <= d <= 10, every feature finite with |x| <= 100; numClasses an int with
2 <= numClasses <= 10; N integer labels with 0 <= y[i] < numClasses; lr a
finite number with 0 < lr <= 10; steps an int with 1 <= steps <= 500.
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(X, y, numClasses, lr, steps):
    if not isinstance(X, list) or not 1 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d or not all(_num(v, 100) for v in row):
            return False
    if not (_int(numClasses) and 2 <= numClasses <= 10):
        return False
    if not isinstance(y, list) or len(y) != len(X) or not all(_int(v) and 0 <= v < numClasses for v in y):
        return False
    if not (_num(lr, 10) and lr > 0):
        return False
    return _int(steps) and 1 <= steps <= 500
