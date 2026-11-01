"""Input-constraint validator for problem 'streaming-weighted-metrics'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks the operation sequence and every stated bound:
- operations and args are aligned lists of length 1..2000
- the constructor `WeightedMetrics` comes exactly once, first, with
  args [threshold], threshold finite in [0, 1]
- every later operation is update, result or reset
- update takes [scores, labels, weights]: three lists of the same length 1..1000;
  each score finite in [1e-6, 1 - 1e-6]; each label the int 0 or 1; each
  weight finite in [0, 100]
- result and reset take []
- at most 10^5 scores in total across all updates
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def validate_input(operations, args):
    if not (isinstance(operations, list) and isinstance(args, list)):
        return False
    if not 1 <= len(operations) <= 2000 or len(args) != len(operations):
        return False
    if operations[0] != "WeightedMetrics" or not isinstance(args[0], list) or len(args[0]) != 1:
        return False
    t = args[0][0]
    if not (_num(t) and 0 <= t <= 1):
        return False
    total = 0
    for op, a in zip(operations[1:], args[1:]):
        if not isinstance(a, list):
            return False
        if op in ("result", "reset"):
            if a:
                return False
        elif op == "update":
            if len(a) != 3 or not all(isinstance(x, list) for x in a):
                return False
            s, y, w = a
            if not 1 <= len(s) <= 1000 or len(y) != len(s) or len(w) != len(s):
                return False
            if not all(_num(p) and 1e-6 <= p <= 1 - 1e-6 for p in s):
                return False
            if not all(isinstance(v, int) and not isinstance(v, bool) and v in (0, 1) for v in y):
                return False
            if not all(_num(v) and 0 <= v <= 100 for v in w):
                return False
            total += len(s)
        else:
            return False
    return total <= 100_000
