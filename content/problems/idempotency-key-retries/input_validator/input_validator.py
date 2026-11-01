"""Input-constraint validator for problem 'idempotency-key-retries'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks the operation sequence and every stated bound:
- operations and args are aligned lists of length 1..2000
- the constructor `IdempotentLedger` comes exactly once, first, with args
  [ttl], ttl an int in [1, 10^9]
- every later operation is charge, balance or failNext
- charge takes [key, account, amount, now]: key and account non-empty strings
  of at most 20 characters, amount an int with |amount| <= 10^6, now an int in
  [0, 10^9], non-decreasing across charge calls
- balance takes [account] (same string rule); failNext takes [mode] with mode
  "before" or "after"
"""


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _name(v):
    return isinstance(v, str) and 1 <= len(v) <= 20


def validate_input(operations, args):
    if not (isinstance(operations, list) and isinstance(args, list)):
        return False
    if not 1 <= len(operations) <= 2000 or len(args) != len(operations):
        return False
    if operations[0] != "IdempotentLedger" or not isinstance(args[0], list) or len(args[0]) != 1:
        return False
    if not _int(args[0][0], 1, 10**9):
        return False
    last = 0
    for op, a in zip(operations[1:], args[1:]):
        if not isinstance(a, list):
            return False
        if op == "charge":
            if len(a) != 4:
                return False
            key, account, amount, now = a
            if not (_name(key) and _name(account) and _int(amount, -10**6, 10**6) and _int(now, 0, 10**9)):
                return False
            if now < last:
                return False
            last = now
        elif op == "balance":
            if len(a) != 1 or not _name(a[0]):
                return False
        elif op == "failNext":
            if len(a) != 1 or a[0] not in ("before", "after"):
                return False
        else:
            return False
    return True
