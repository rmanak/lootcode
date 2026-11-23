"""Input-constraint validator for problem 'rotary-position-embedding'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: x is T x d with 1 <= T <= 64 and d even in
[2, 64], entries finite with |v| <= 10; positions has T ints in [0, 10^5];
base a finite number in [2, 10^6]; style "interleaved" or "half". No bools.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def validate_input(x, positions, base, style):
    if not isinstance(x, list) or not 1 <= len(x) <= 64 or not isinstance(x[0], list):
        return False
    d = len(x[0])
    if not (2 <= d <= 64 and d % 2 == 0):
        return False
    if not all(isinstance(r, list) and len(r) == d and all(_num(v, -10, 10) for v in r) for r in x):
        return False
    if not (isinstance(positions, list) and len(positions) == len(x)
            and all(isinstance(p, int) and not isinstance(p, bool) and 0 <= p <= 100_000 for p in positions)):
        return False
    return _num(base, 2, 1_000_000) and style in ("interleaved", "half")
