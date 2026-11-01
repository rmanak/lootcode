"""Input-constraint validator for problem 'decision-tree-best-split'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is N x d with 2 <= N <= 500 and 1 <= d <= 10,
every entry a finite number with |x| <= 10^4; y has N int labels with
0 <= label <= 9. It also enforces the statement's promise that at least one
feature takes two or more distinct values, so a split exists.
"""
import math


def validate_input(X, y):
    if not isinstance(X, list) or not 2 <= len(X) <= 500 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d:
            return False
        for v in row:
            if (not isinstance(v, (int, float)) or isinstance(v, bool)
                    or not math.isfinite(v) or abs(v) > 10_000):
                return False
    if not isinstance(y, list) or len(y) != len(X):
        return False
    if not all(isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 9 for v in y):
        return False
    return any(len({row[j] for row in X}) > 1 for j in range(d))
