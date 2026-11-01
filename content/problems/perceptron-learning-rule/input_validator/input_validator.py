"""Input-constraint validator for problem 'perceptron-learning-rule'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 rows of the same length d with
1 <= d <= 10, every feature an int with |x| <= 100; N labels each exactly 1 or
-1 (ints); maxEpochs an int with 1 <= maxEpochs <= 100.
"""


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(X, y, maxEpochs):
    if not isinstance(X, list) or not 1 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d or not all(_int(v) and abs(v) <= 100 for v in row):
            return False
    if not isinstance(y, list) or len(y) != len(X) or not all(_int(v) and v in (1, -1) for v in y):
        return False
    return _int(maxEpochs) and 1 <= maxEpochs <= 100
