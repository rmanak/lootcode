"""Input-constraint validator for problem 'top-k-top-p-sampling'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= V <= 1000 logits, each a finite number with
|logit| <= 100; 0.01 <= temperature <= 100; topK an int with 1 <= topK <= V;
0 < topP <= 1; 0 <= u < 1. Ties are pinned by the statement, so nothing more
is promised about the answer.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_input(logits, temperature, topK, topP, u):
    if not isinstance(logits, list) or not 1 <= len(logits) <= 1000:
        return False
    if not all(_num(x) and abs(x) <= 100 for x in logits):
        return False
    if not (_num(temperature) and 0.01 <= temperature <= 100):
        return False
    if not (isinstance(topK, int) and not isinstance(topK, bool) and 1 <= topK <= len(logits)):
        return False
    if not (_num(topP) and 0 < topP <= 1):
        return False
    return _num(u) and 0 <= u < 1
