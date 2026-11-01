"""Input-constraint validator for problem 'standard-scaler-and-one-hot'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: columnTypes a list of 1 <= D <= 10 strings, each
"numeric" or "categorical"; train has 1..200 rows and test 1..200 rows, each a
list of D values. In a numeric column every value is None or a finite number
(not bool) with |v| <= 10^6, and at least one train value is not None. In a
categorical column every value is None or a string of 1..10 ASCII letters or
digits. It also enforces the promise that a non-constant numeric column's
population standard deviation over train is at least 1e-3.
"""
import math


def _num(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= 10**6)


def _cat(v):
    return isinstance(v, str) and 1 <= len(v) <= 10 and v.isascii() and v.isalnum()


def validate_input(train, test, columnTypes):
    if not isinstance(columnTypes, list) or not 1 <= len(columnTypes) <= 10:
        return False
    if not all(t in ("numeric", "categorical") for t in columnTypes):
        return False
    D = len(columnTypes)
    for rows in (train, test):
        if not isinstance(rows, list) or not 1 <= len(rows) <= 200:
            return False
        for r in rows:
            if not isinstance(r, list) or len(r) != D:
                return False
            for v, t in zip(r, columnTypes):
                if v is not None and not (_num(v) if t == "numeric" else _cat(v)):
                    return False
    for j, t in enumerate(columnTypes):
        if t != "numeric":
            continue
        seen = [r[j] for r in train if r[j] is not None]
        if not seen:
            return False
        if any(v != seen[0] for v in seen):
            mean = math.fsum(seen) / len(seen)
            if math.sqrt(math.fsum((v - mean) ** 2 for v in seen) / len(seen)) < 1e-3:
                return False
    return True
