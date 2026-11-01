"""Input-constraint validator for problem 'merge-partial-softmax-blocks'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1..200 queries, each a list of 1..64 blocks
[m, l, o]; within a query every o has the same length d in [1, 64]; a masked
block has m = null, l = 0 and o all zeros; a live block has finite m with
|m| <= 10^4, finite l in [1, 10^6] and finite o entries with |o| <= 100; at
most 2 * 10^5 numbers in all the o vectors together. No bools as numbers.
"""
import math


def _num(v, lim):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= lim


def validate_input(queries):
    if not isinstance(queries, list) or not 1 <= len(queries) <= 200:
        return False
    total = 0
    for blocks in queries:
        if not isinstance(blocks, list) or not 1 <= len(blocks) <= 64:
            return False
        d = None
        for b in blocks:
            if not (isinstance(b, list) and len(b) == 3 and isinstance(b[2], list)):
                return False
            m, l, o = b
            if d is None:
                d = len(o)
                if not 1 <= d <= 64:
                    return False
            if len(o) != d:
                return False
            total += d
            if m is None:
                if not (_num(l, 0) and l == 0 and all(_num(v, 0) for v in o)):
                    return False
            else:
                if not (_num(m, 1e4) and _num(l, 1e6) and l >= 1 and all(_num(v, 100) for v in o)):
                    return False
    return total <= 2 * 10**5
