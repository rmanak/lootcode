"""Input-constraint validator for problem 'speculative-decoding-acceptance'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: k = len(draftTokens) in [1, 16]; draftProbs is
k x V and targetProbs (k+1) x V with 2 <= V <= 1000; every probability finite
in [0, 1] and every row summing to 1 within 1e-9; each draft token an int in
[0, V) with draftProbs[i][token] > 0; u has k entries and uSample is one
number, all finite in [0, 1). No bools.

Not checked here: the margin promises (no u[i] within 1e-9 of p/q, no
inverse-CDF threshold within 1e-9 of a cumulative sum, unless exactly equal
with power-of-two denominators). The case generator vets those.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def _dist(row, V):
    return (isinstance(row, list) and len(row) == V and all(_num(v, 0, 1) for v in row)
            and abs(math.fsum(row) - 1) <= 1e-9)


def validate_input(draftTokens, draftProbs, targetProbs, u, uSample):
    if not isinstance(draftTokens, list) or not 1 <= len(draftTokens) <= 16:
        return False
    k = len(draftTokens)
    if not (isinstance(draftProbs, list) and len(draftProbs) == k and isinstance(draftProbs[0], list)):
        return False
    V = len(draftProbs[0])
    if not 2 <= V <= 1000:
        return False
    if not all(_dist(r, V) for r in draftProbs):
        return False
    if not (isinstance(targetProbs, list) and len(targetProbs) == k + 1 and all(_dist(r, V) for r in targetProbs)):
        return False
    for i, x in enumerate(draftTokens):
        if not (isinstance(x, int) and not isinstance(x, bool) and 0 <= x < V and draftProbs[i][x] > 0):
            return False
    if not (isinstance(u, list) and len(u) == k and all(_num(v, 0, 1) and v < 1 for v in u)):
        return False
    return _num(uSample, 0, 1) and uSample < 1
