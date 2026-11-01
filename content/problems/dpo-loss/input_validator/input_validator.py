"""Input-constraint validator for problem 'dpo-loss'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: the four log-prob lists have the same length
1..1000, every value finite (not a bool) in [-10^4, 0]; beta finite in
(0, 10]; labelSmoothing finite in [0, 0.5), and exactly 0 when lossType is
"ipo"; lossType "sigmoid" or "ipo".

Not checked here: the promise that each pair's two implicit rewards are either
exactly equal (with both floating-point subtractions exact) or differ by more
than 1e-9 relative. The case generator vets that in exact arithmetic.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def validate_input(policyChosen, policyRejected, refChosen, refRejected, beta, labelSmoothing, lossType):
    lists = (policyChosen, policyRejected, refChosen, refRejected)
    if not all(isinstance(a, list) for a in lists):
        return False
    n = len(policyChosen)
    if not 1 <= n <= 1000 or any(len(a) != n for a in lists):
        return False
    if not all(_num(v, -10_000, 0) for a in lists for v in a):
        return False
    if not (_num(beta, 0, 10) and beta > 0):
        return False
    if lossType not in ("sigmoid", "ipo"):
        return False
    if not (_num(labelSmoothing, 0, 0.5) and labelSmoothing < 0.5):
        return False
    return lossType == "sigmoid" or labelSmoothing == 0
