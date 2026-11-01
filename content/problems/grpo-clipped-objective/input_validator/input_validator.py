"""Input-constraint validator for problem 'grpo-clipped-objective'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: rewards is B x G with 1 <= B <= 8 and
2 <= G <= 16, every reward finite with |r| <= 100; newLogps, oldLogps and
refLogps each hold B*G lists, the three aligned in length (1..64 tokens per
completion), every value finite in [-50, 0]; clipEps finite in (0, 0.5];
beta finite in [0, 1]; aggregation "sequence" or "token". No bools.

Not checked here: the promises that keep clipFraction unambiguous (each
advantage exactly 0 or at least 1e-9 in size; each ratio at least 1e-9 away
from 1 - clipEps and 1 + clipEps). The case generator vets those.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def validate_input(rewards, newLogps, oldLogps, refLogps, clipEps, beta, aggregation):
    if not isinstance(rewards, list) or not 1 <= len(rewards) <= 8 or not isinstance(rewards[0], list):
        return False
    g = len(rewards[0])
    if not 2 <= g <= 16:
        return False
    if not all(isinstance(r, list) and len(r) == g and all(_num(v, -100, 100) for v in r) for r in rewards):
        return False
    n = len(rewards) * g
    for seqs in (newLogps, oldLogps, refLogps):
        if not isinstance(seqs, list) or len(seqs) != n:
            return False
    for a, b, c in zip(newLogps, oldLogps, refLogps):
        if not (isinstance(a, list) and isinstance(b, list) and isinstance(c, list)):
            return False
        if not 1 <= len(a) <= 64 or len(b) != len(a) or len(c) != len(a):
            return False
        if not all(_num(v, -50, 0) for v in a + b + c):
            return False
    return (_num(clipEps, 0, 0.5) and clipEps > 0 and _num(beta, 0, 1)
            and aggregation in ("sequence", "token"))
