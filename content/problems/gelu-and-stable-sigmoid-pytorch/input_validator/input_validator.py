"""Input-constraint validator for problem 'gelu-and-stable-sigmoid'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: x a list of 1 <= N <= 10^4 finite numbers (not
bools) with |x| <= 1000.
"""
import math


def validate_input(x):
    if not isinstance(x, list) or not 1 <= len(x) <= 10_000:
        return False
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
               and abs(v) <= 1000 for v in x)
