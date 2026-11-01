"""Input-constraint validator for problem 'k-nearest-neighbors-classifier'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 1000 training rows and 1 <= M <= 200 test
rows, all of the same length d with 1 <= d <= 20, every coordinate a finite
number with |x| <= 1000; exactly N labels, each an int (not a bool) with
0 <= label <= 100; and k an int with 1 <= k <= N. Ties are resolved by rules
the statement pins, so the answer needs no further promise.
"""
import math

MAX_N, MAX_M, MAX_D, MAX_ABS, MAX_LABEL = 1000, 200, 20, 1000, 100


def _rows(a, max_rows, d):
    if not isinstance(a, list) or not 1 <= len(a) <= max_rows:
        return False
    for row in a:
        if not isinstance(row, list) or len(row) != d:
            return False
        for v in row:
            if (not isinstance(v, (int, float)) or isinstance(v, bool)
                    or not math.isfinite(v) or abs(v) > MAX_ABS):
                return False
    return True


def validate_input(trainX, trainY, testX, k):
    if not isinstance(trainX, list) or not trainX or not isinstance(trainX[0], list):
        return False
    d = len(trainX[0])
    if not 1 <= d <= MAX_D:
        return False
    if not _rows(trainX, MAX_N, d) or not _rows(testX, MAX_M, d):
        return False
    if not isinstance(trainY, list) or len(trainY) != len(trainX):
        return False
    if not all(isinstance(y, int) and not isinstance(y, bool) and 0 <= y <= MAX_LABEL
               for y in trainY):
        return False
    return isinstance(k, int) and not isinstance(k, bool) and 1 <= k <= len(trainX)
