"""Input-constraint validator for problem 'pairwise-ranker-ii-training'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 pairs, each a pair of equal-length
vectors with 1 <= d <= 10, every feature value a finite number with
|value| <= 10, 0 < lr <= 1, and an integer 0 <= steps <= 1000.

NOT checkable here: that a case is well-conditioned — that gradient descent
from w = 0 doesn't amplify last-bit float differences into a visible change in
w. Each stored case was vetted for that when it was generated (it agrees with
independently written implementations and survives a 1e-12 perturbation of
every step), and any new case must be vetted the same way; see the
"Machine-learning problems" section of specs/problem-authoring-guidelines.md.
"""
import math

MAX_PAIRS = 200
MAX_DIM = 10
MAX_ABS = 10
MAX_STEPS = 1000


def _number(x, bound):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x) and abs(x) <= bound)


def validate_input(preferences, lr, steps):
    if not isinstance(preferences, list) or not 1 <= len(preferences) <= MAX_PAIRS:
        return False
    first = preferences[0]
    if not isinstance(first, list) or len(first) != 2 or not isinstance(first[0], list):
        return False
    d = len(first[0])
    if not 1 <= d <= MAX_DIM:
        return False
    for pair in preferences:
        if not isinstance(pair, list) or len(pair) != 2:
            return False
        for v in pair:
            if not isinstance(v, list) or len(v) != d:
                return False
            if not all(_number(x, MAX_ABS) for x in v):
                return False
    if not _number(lr, 1) or lr <= 0:
        return False
    if isinstance(steps, bool) or not isinstance(steps, int):
        return False
    return 0 <= steps <= MAX_STEPS
