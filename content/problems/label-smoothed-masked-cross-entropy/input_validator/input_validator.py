"""Input-constraint validator for problem 'label-smoothed-masked-cross-entropy'.

Hand-written. logits is N x C (1 <= N <= 500, 2 <= C <= 100), every value
finite (not a bool) with |z| <= 1000; targets N ints in [0, C); mask N ints
each 0 or 1; smoothing a number in [0, 1).
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(logits, targets, mask, smoothing):
    if not isinstance(logits, list) or not 1 <= len(logits) <= 500 or not isinstance(logits[0], list):
        return False
    N, C = len(logits), len(logits[0])
    if not 2 <= C <= 100:
        return False
    for r in logits:
        if not isinstance(r, list) or len(r) != C:
            return False
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 1000 for v in r):
            return False
    if not isinstance(targets, list) or len(targets) != N or not all(_int(t) and 0 <= t < C for t in targets):
        return False
    if not isinstance(mask, list) or len(mask) != N or not all(_int(v) and v in (0, 1) for v in mask):
        return False
    return (isinstance(smoothing, (int, float)) and not isinstance(smoothing, bool)
            and math.isfinite(smoothing) and 0 <= smoothing < 1)
