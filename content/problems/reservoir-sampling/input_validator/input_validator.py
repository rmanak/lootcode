"""Input-constraint validator for problem 'reservoir-sampling'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks the operation sequence and every stated bound:
- operations and args are aligned lists of length 1..20001
- the constructor `ReservoirSampler` comes exactly once, first, with args [k],
  k an int in [1, 100]
- every later operation is add or sample
- add takes [item, u]: item an int with |item| <= 10^9, and u a finite float
  (or the int 0) with 0 <= u < 1
- sample takes []
- at most 10^4 add calls

Not checked here: that u * i never lands within 1e-9 of an integer unless it
equals one exactly. The case generator vets that with exact Fractions.
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(operations, args):
    if not (isinstance(operations, list) and isinstance(args, list)):
        return False
    if not 1 <= len(operations) <= 20_001 or len(args) != len(operations):
        return False
    if operations[0] != "ReservoirSampler" or not isinstance(args[0], list) or len(args[0]) != 1:
        return False
    if not (_int(args[0][0]) and 1 <= args[0][0] <= 100):
        return False
    adds = 0
    for op, a in zip(operations[1:], args[1:]):
        if not isinstance(a, list):
            return False
        if op == "sample":
            if a:
                return False
        elif op == "add":
            if len(a) != 2:
                return False
            item, u = a
            if not (_int(item) and abs(item) <= 10**9):
                return False
            if not (isinstance(u, (int, float)) and not isinstance(u, bool) and math.isfinite(u) and 0 <= u < 1):
                return False
            adds += 1
        else:
            return False
    return adds <= 10_000
