"""Input-constraint validator for problem 'binary-classification-metrics'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 10^4 scores, each finite with
|s| <= 10^3; N labels, each the int 0 or 1; threshold finite with
|threshold| <= 10^3.
"""
import math


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def validate_input(scores, labels, threshold):
    if not isinstance(scores, list) or not 1 <= len(scores) <= 10_000:
        return False
    if not all(_num(s, 1000) for s in scores):
        return False
    if not isinstance(labels, list) or len(labels) != len(scores):
        return False
    if not all(isinstance(v, int) and not isinstance(v, bool) and v in (0, 1) for v in labels):
        return False
    return _num(threshold, 1000)
