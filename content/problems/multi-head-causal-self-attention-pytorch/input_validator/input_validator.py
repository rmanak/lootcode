"""Input-constraint validator for problem 'multi-head-causal-self-attention'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is T x D with 1 <= T <= 32 and 1 <= D <= 32;
Wq, Wk, Wv and Wo are each D x D; every entry of X and the weights is a finite
number with |x| <= 10; numHeads is an int with 1 <= numHeads <= D that divides
D exactly (the statement's promise that the heads split D evenly).
"""
import math

MAX_T, MAX_D, MAX_ABS = 32, 32, 10


def _matrix(a, rows, cols):
    if not isinstance(a, list) or len(a) != rows:
        return False
    for row in a:
        if not isinstance(row, list) or len(row) != cols:
            return False
        for x in row:
            if (not isinstance(x, (int, float)) or isinstance(x, bool)
                    or not math.isfinite(x) or abs(x) > MAX_ABS):
                return False
    return True


def validate_input(X, Wq, Wk, Wv, Wo, numHeads):
    if not isinstance(X, list) or not 1 <= len(X) <= MAX_T:
        return False
    if not isinstance(X[0], list) or not 1 <= len(X[0]) <= MAX_D:
        return False
    T, D = len(X), len(X[0])
    if not _matrix(X, T, D):
        return False
    if not all(_matrix(W, D, D) for W in (Wq, Wk, Wv, Wo)):
        return False
    return (isinstance(numHeads, int) and not isinstance(numHeads, bool)
            and 1 <= numHeads <= D and D % numHeads == 0)
