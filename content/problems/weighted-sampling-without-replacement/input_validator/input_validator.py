"""Input-constraint validator for problem 'weighted-sampling-without-replacement'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: weights a list of 1 <= N <= 10^4 finite numbers with
1e-4 <= w <= 10^4; k an int with 1 <= k <= N; u a list of N finite numbers
with 0 < u < 1.

Not checked here: the promise that keys that decide the answer are never within
a relative 1e-9 of each other unless their (u, w) pairs are identical. The
case generator vets that.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_input(weights, k, u):
    if not isinstance(weights, list) or not 1 <= len(weights) <= 10_000:
        return False
    if not all(_num(w) and 1e-4 <= w <= 10_000 for w in weights):
        return False
    if not (isinstance(k, int) and not isinstance(k, bool) and 1 <= k <= len(weights)):
        return False
    return isinstance(u, list) and len(u) == len(weights) and all(_num(x) and 0 < x < 1 for x in u)
