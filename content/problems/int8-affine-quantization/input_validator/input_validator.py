"""Input-constraint validator for problem 'int8-affine-quantization'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: calibration and x are lists of 1..10^4 finite
numbers (not bools) with |v| <= 10^4.

Not checked here: the promise that every value of x / scale, and
-128 - rmin / scale, is either exactly halfway between two integers or at
least 1e-6 away from halfway. The case generator vets that in exact
arithmetic.
"""
import math


def _nums(a):
    return (isinstance(a, list) and 1 <= len(a) <= 10_000
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
                    and abs(v) <= 10_000 for v in a))


def validate_input(calibration, x):
    return _nums(calibration) and _nums(x)
