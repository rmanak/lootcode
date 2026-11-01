"""Input-constraint validator for problem 'softmax-cross-entropy-loss-and-gradient'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 100 rows, every row the same length C with
2 <= C <= 20, every logit a finite number with |logit| <= 1000, and exactly N
labels, each an integer (not a bool) with 0 <= label < C. The problem makes no
promise about the answer, so there is nothing further to enforce.
"""
import math

MAX_N = 100
MIN_C, MAX_C = 2, 20
MAX_ABS = 1000


def _number(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x) and abs(x) <= MAX_ABS)


def validate_input(logits, labels):
    if not isinstance(logits, list) or not 1 <= len(logits) <= MAX_N:
        return False
    if not isinstance(labels, list) or len(labels) != len(logits):
        return False
    first = logits[0]
    if not isinstance(first, list) or not MIN_C <= len(first) <= MAX_C:
        return False
    c = len(first)
    for row in logits:
        if not isinstance(row, list) or len(row) != c:
            return False
        if not all(_number(x) for x in row):
            return False
    return all(isinstance(y, int) and not isinstance(y, bool) and 0 <= y < c
               for y in labels)
