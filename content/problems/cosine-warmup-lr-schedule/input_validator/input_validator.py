"""Input-constraint validator for problem 'cosine-warmup-lr-schedule'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: steps a list of 1..10^4 ints in [0, 2*10^6];
0 <= minLr <= baseLr <= 10 (finite numbers); warmupSteps and totalSteps ints
with 0 <= warmupSteps < totalSteps <= 10^6. No bools.
"""
import math


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_input(steps, baseLr, minLr, warmupSteps, totalSteps):
    if not isinstance(steps, list) or not 1 <= len(steps) <= 10_000:
        return False
    if not all(_int(t, 0, 2_000_000) for t in steps):
        return False
    if not (_num(baseLr) and _num(minLr) and 0 <= minLr <= baseLr <= 10):
        return False
    return _int(totalSteps, 1, 1_000_000) and _int(warmupSteps, 0, totalSteps - 1)
