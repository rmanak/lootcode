"""Input-constraint validator for problem 'sinusoidal-positional-encoding'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: positions a list of 1..100 ints in [0, 10^5]; d an
int in [1, 128]; base a finite number in [2, 10^6]. No bools.
"""
import math


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def validate_input(positions, d, base):
    if not isinstance(positions, list) or not 1 <= len(positions) <= 100:
        return False
    if not all(_int(p, 0, 100_000) for p in positions):
        return False
    return (_int(d, 1, 128) and isinstance(base, (int, float)) and not isinstance(base, bool)
            and math.isfinite(base) and 2 <= base <= 1_000_000)
