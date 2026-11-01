"""Input-constraint validator for problem 'pairwise-ranker-i-loss-and-gradient'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 pairs, each a pair of equal-length
vectors with 1 <= d <= 20, len(w) == d, and every feature value and weight a
finite number with |value| <= 100. The problem makes no promise about the
answer, so there is nothing further to enforce.
"""
import math

MAX_PAIRS = 200
MAX_DIM = 20
MAX_ABS = 100


def _number(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x) and abs(x) <= MAX_ABS)


def _vector(v, d):
    return isinstance(v, list) and len(v) == d and all(_number(x) for x in v)


def validate_input(preferences, w):
    if not isinstance(preferences, list) or not 1 <= len(preferences) <= MAX_PAIRS:
        return False
    if not isinstance(w, list) or not 1 <= len(w) <= MAX_DIM:
        return False
    d = len(w)
    for pair in preferences:
        if not isinstance(pair, list) or len(pair) != 2:
            return False
        if not (_vector(pair[0], d) and _vector(pair[1], d)):
            return False
    return _vector(w, d)
