"""Input-constraint validator for problem 'scaled-dot-product-attention'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: Q is n x dk, K is m x dk, V is m x dv and mask is
n x m, with 1 <= n, m <= 64 and 1 <= dk, dv <= 32; every number in Q, K and V
is finite with |x| <= 100; every mask entry is the int 0 or 1. It also
enforces the statement's promise that every row of mask contains at least one
1, so no query is left with nothing to attend to.
"""
import math

MAX_ROWS, MAX_DIM, MAX_ABS = 64, 32, 100


def _matrix(a, max_rows):
    """(rows, cols) of a rectangular, in-range numeric matrix, else None."""
    if not isinstance(a, list) or not 1 <= len(a) <= max_rows:
        return None
    if not isinstance(a[0], list) or not 1 <= len(a[0]) <= MAX_DIM:
        return None
    c = len(a[0])
    for row in a:
        if not isinstance(row, list) or len(row) != c:
            return None
        for x in row:
            if (not isinstance(x, (int, float)) or isinstance(x, bool)
                    or not math.isfinite(x) or abs(x) > MAX_ABS):
                return None
    return len(a), c


def validate_input(Q, K, V, mask):
    q = _matrix(Q, MAX_ROWS)
    k = _matrix(K, MAX_ROWS)
    v = _matrix(V, MAX_ROWS)
    if q is None or k is None or v is None:
        return False
    n, dk = q
    m, dk2 = k
    if dk2 != dk or v[0] != m:
        return False
    if not isinstance(mask, list) or len(mask) != n:
        return False
    for row in mask:
        if not isinstance(row, list) or len(row) != m:
            return False
        if not all(isinstance(x, int) and not isinstance(x, bool) and x in (0, 1) for x in row):
            return False
        if 1 not in row:
            return False
    return True
