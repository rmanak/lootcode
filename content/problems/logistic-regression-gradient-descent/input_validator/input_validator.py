"""Input-constraint validator for problem 'logistic-regression-gradient-descent'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 rows, every row the same length d with
1 <= d <= 10, every feature a finite number with |x| <= 100, exactly N labels
each 0 or 1 (ints, not bools), 0 < lr <= 10 a finite number, and
1 <= steps <= 1000 an int. The statement promises nothing about the answer.
"""
import math

MAX_N, MAX_D, MAX_ABS = 200, 10, 100
MAX_LR, MAX_STEPS = 10, 1000


def _number(x, bound):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x) and abs(x) <= bound)


def validate_input(X, y, lr, steps):
    if not isinstance(X, list) or not 1 <= len(X) <= MAX_N:
        return False
    if not isinstance(y, list) or len(y) != len(X):
        return False
    if not isinstance(X[0], list) or not 1 <= len(X[0]) <= MAX_D:
        return False
    d = len(X[0])
    for row in X:
        if not isinstance(row, list) or len(row) != d:
            return False
        if not all(_number(v, MAX_ABS) for v in row):
            return False
    if not all(isinstance(v, int) and not isinstance(v, bool) and v in (0, 1) for v in y):
        return False
    if not _number(lr, MAX_LR) or lr <= 0:
        return False
    return isinstance(steps, int) and not isinstance(steps, bool) and 1 <= steps <= MAX_STEPS
