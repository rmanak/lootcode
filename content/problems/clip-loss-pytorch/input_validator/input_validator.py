"""Input-constraint validator for problem 'clip-loss-pytorch'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. This is a torch-runtime problem, so
the checker (scripts/check_constraint_validators.py) first makes each test
input concrete: tensors arrive here as plain nested lists. It also runs the
validator over draws from the problem's random-test generator, so every input
the grader can produce is held to the same constraints.
See docs/input-validators.md and docs/torch-runtime.md.

Checks every stated bound: image_feat and text_feat are both N x D with
1 <= N <= 64 and 1 <= D <= 128; every entry is finite with |x| <= 100; every
row has an L2 norm of at least 1e-3 (normalization is well defined); and
temperature is a finite number with 0.01 <= temperature <= 10. The statement
makes no promise about the answer.
"""
import math

MAX_N, MAX_D = 64, 128
MIN_ROW_NORM = 1e-3


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def _features(a, rows=None):
    if not isinstance(a, list) or not 1 <= len(a) <= MAX_N:
        return False
    if rows is not None and len(a) != rows:
        return False
    if not all(isinstance(r, list) for r in a):
        return False
    d = len(a[0])
    if not 1 <= d <= MAX_D:
        return False
    for r in a:
        if len(r) != d or not all(_num(v, 100) for v in r):
            return False
        if math.sqrt(sum(v * v for v in r)) < MIN_ROW_NORM:
            return False
    return True


def validate_input(image_feat, text_feat, temperature):
    if not (_features(image_feat) and _features(text_feat, rows=len(image_feat))):
        return False
    if len(image_feat[0]) != len(text_feat[0]):
        return False
    return _num(temperature, 10) and temperature >= 0.01
