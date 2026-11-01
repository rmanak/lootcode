"""Input-constraint validator for problem 'multinomial-naive-bayes'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: trainX has 1 <= N <= 200 rows and testX 1 <= M <= 100
rows, all of the same length V with 1 <= V <= 50, every count an int in
[0, 100]; trainY has N int labels in [0, 9], and every label from 0 to
max(trainY) appears at least once; alpha finite with 0 < alpha <= 10.

Not checked here: the promise that the top two classes' joint log-probabilities
are either identical (tied classes with identical data) or more than 1e-6
apart. The case generator vets that.
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _rows(M, lo, hi, width):
    if not isinstance(M, list) or not lo <= len(M) <= hi:
        return False
    return all(isinstance(r, list) and len(r) == width and all(_int(v) and 0 <= v <= 100 for v in r)
               for r in M)


def validate_input(trainX, trainY, testX, alpha):
    if not isinstance(trainX, list) or not trainX or not isinstance(trainX[0], list):
        return False
    V = len(trainX[0])
    if not 1 <= V <= 50:
        return False
    if not (_rows(trainX, 1, 200, V) and _rows(testX, 1, 100, V)):
        return False
    if not isinstance(trainY, list) or len(trainY) != len(trainX):
        return False
    if not all(_int(v) and 0 <= v <= 9 for v in trainY):
        return False
    if set(trainY) != set(range(max(trainY) + 1)):
        return False
    return (isinstance(alpha, (int, float)) and not isinstance(alpha, bool)
            and math.isfinite(alpha) and 0 < alpha <= 10)
