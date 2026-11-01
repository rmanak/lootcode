"""Input-constraint validator for problem 'symmetric-2x2-eigen'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1..200 matrices, each [[a, b], [b, c]] (2 x 2 and
exactly symmetric), every entry finite (not a bool) with |v| <= 10^8.

Not checked here: the separation promises for matrices with b != 0 (the
eigenvalues differ by at least 1e-6 times the larger magnitude, and v1's
first component is at least 1e-6). The case generator vets them.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 1e8


def validate_input(matrices):
    if not isinstance(matrices, list) or not 1 <= len(matrices) <= 200:
        return False
    for M in matrices:
        if not (isinstance(M, list) and len(M) == 2 and all(isinstance(r, list) and len(r) == 2 for r in M)):
            return False
        if not all(_num(v) for r in M for v in r):
            return False
        if M[0][1] != M[1][0]:
            return False
    return True
