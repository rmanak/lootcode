"""Input-constraint validator for problem 'gradient-clipping-by-global-norm'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: grads a list of 1..50 non-empty lists, at most
10^4 numbers in total, each finite (not a bool) with |v| <= 1e200; maxNorm a
finite number with 0 < maxNorm <= 1e6.
"""
import math


def _num(v, bound):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= bound


def validate_input(grads, maxNorm):
    if not isinstance(grads, list) or not 1 <= len(grads) <= 50:
        return False
    total = 0
    for g in grads:
        if not isinstance(g, list) or not g or not all(_num(v, 1e200) for v in g):
            return False
        total += len(g)
    return total <= 10_000 and _num(maxNorm, 1e6) and maxNorm > 0
