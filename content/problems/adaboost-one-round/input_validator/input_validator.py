"""Input-constraint validator for problem 'adaboost-one-round'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 2 <= N <= 200 rows of the same length d with
1 <= d <= 10, every feature finite with |x| <= 10^4; N labels each exactly 1 or
-1 (ints); N finite weights with 1e-6 <= w <= 100. It also enforces two
promises: at least one feature takes two or more distinct values, and the best
stump's weighted error (as a fraction of the total weight) is at least 1e-3,
so alpha is finite. It brute-forces every stump to check that.

Not checked here: the tie promise (any error not tied with the best trails it
by more than 1e-6). The case generator vets that with exact Fractions.
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(X, y, weights):
    if not isinstance(X, list) or not 2 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d or not all(_num(v, 10_000) for v in row):
            return False
    if not isinstance(y, list) or len(y) != len(X) or not all(_int(v) and v in (1, -1) for v in y):
        return False
    if not isinstance(weights, list) or len(weights) != len(X):
        return False
    if not all(_num(v, 100) and v >= 1e-6 for v in weights):
        return False
    total = math.fsum(weights)
    best = None
    for j in range(d):
        pairs = sorted(zip((r[j] for r in X), y, weights))
        left_pos = 0.0
        right_neg = math.fsum(w for _, lab, w in pairs if lab < 0)
        for i in range(len(pairs) - 1):
            _, lab, w = pairs[i]
            if lab > 0:
                left_pos += w
            else:
                right_neg -= w
            if pairs[i][0] == pairs[i + 1][0]:
                continue
            e = (left_pos + right_neg) / total
            e = min(e, 1 - e)
            best = e if best is None else min(best, e)
    return best is not None and best >= 1e-3
