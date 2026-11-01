"""Input-constraint validator for problem 'roc-auc'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 2 <= N <= 50000 with len(scores) == len(labels),
every score a finite number with |score| <= 10**6, and every label the integer
0 or 1 (not a bool). Also enforces the statement's promise that both classes
occur at least once, without which the AUC is 0/0.
"""
import math

MAX_N = 50_000
MAX_ABS = 10**6


def validate_input(scores, labels):
    if not isinstance(scores, list) or not isinstance(labels, list):
        return False
    if not 2 <= len(scores) <= MAX_N or len(labels) != len(scores):
        return False
    for s in scores:
        if not (isinstance(s, (int, float)) and not isinstance(s, bool)
                and math.isfinite(s) and abs(s) <= MAX_ABS):
            return False
    for y in labels:
        if isinstance(y, bool) or y not in (0, 1) or not isinstance(y, int):
            return False
    return 0 in labels and 1 in labels
