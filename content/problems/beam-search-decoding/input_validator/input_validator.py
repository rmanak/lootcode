"""Input-constraint validator for problem 'beam-search-decoding'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: logProbs is a V x V table with 2 <= V <= 50 whose
entries are finite numbers with -100 <= entry <= 0 (log-probabilities); the
tokens startToken and eosToken are ints in [0, V); beamWidth is an int with
1 <= beamWidth <= 10; maxLen is an int with 1 <= maxLen <= 20. The statement
pins every tie, so it makes no further promise about the answer.
"""
import math

MAX_V, MAX_BEAM, MAX_LEN, MIN_LP = 50, 10, 20, -100


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def validate_input(logProbs, startToken, eosToken, beamWidth, maxLen):
    if not isinstance(logProbs, list) or not 2 <= len(logProbs) <= MAX_V:
        return False
    v = len(logProbs)
    for row in logProbs:
        if not isinstance(row, list) or len(row) != v:
            return False
        for x in row:
            if (not isinstance(x, (int, float)) or isinstance(x, bool)
                    or not math.isfinite(x) or not MIN_LP <= x <= 0):
                return False
    return (_int(startToken, 0, v - 1) and _int(eosToken, 0, v - 1)
            and _int(beamWidth, 1, MAX_BEAM) and _int(maxLen, 1, MAX_LEN))
