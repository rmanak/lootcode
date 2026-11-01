"""Input-constraint validator for problem 'stratified-k-fold-indices'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: labels a list of 2 <= N <= 10^4 ints in [0, 10^6];
k an int with 2 <= k <= min(N, 100); perm a permutation of 0..N-1 (N ints, each
index exactly once).
"""


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(labels, k, perm):
    if not isinstance(labels, list) or not 2 <= len(labels) <= 10_000:
        return False
    if not all(_int(v) and 0 <= v <= 10**6 for v in labels):
        return False
    n = len(labels)
    if not (_int(k) and 2 <= k <= min(n, 100)):
        return False
    return (isinstance(perm, list) and len(perm) == n and all(_int(v) for v in perm)
            and sorted(perm) == list(range(n)))
