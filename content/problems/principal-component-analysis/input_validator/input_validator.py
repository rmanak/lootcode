"""Input-constraint validator for problem 'principal-component-analysis'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is N x d with 2 <= N <= 200 and 1 <= d <= 10,
every entry a finite number with |x| <= 1000, and k an int with 1 <= k <= d.

It also enforces the statement's promises about the answer, which make the
components unique (numpy is used for the eigendecomposition):
  * the k largest eigenvalues of the covariance are distinct, and the k-th is
    strictly above the (k+1)-th: every gap between consecutive eigenvalues
    among the top min(k+1, d) is at least 1e-3 times the largest eigenvalue,
    and the largest is positive;
  * in each of the top-k eigenvectors, the largest-magnitude entry beats the
    runner-up by at least 1e-6 (so the sign rule picks one entry).
"""
import math

import numpy as np

GAP, ENTRY_MARGIN = 1e-3, 1e-6


def validate_input(X, k):
    if not isinstance(X, list) or not 2 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 10:
        return False
    for row in X:
        if not isinstance(row, list) or len(row) != d:
            return False
        for v in row:
            if (not isinstance(v, (int, float)) or isinstance(v, bool)
                    or not math.isfinite(v) or abs(v) > 1000):
                return False
    if not (isinstance(k, int) and not isinstance(k, bool) and 1 <= k <= d):
        return False
    A = np.asarray(X, dtype=float)
    Ac = A - A.mean(axis=0)
    vals, vecs = np.linalg.eigh(Ac.T @ Ac / (len(A) - 1))
    vals, vecs = vals[::-1], vecs[:, ::-1]
    if vals[0] <= 0:
        return False
    m = min(k + 1, d)
    if any(vals[i] - vals[i + 1] < GAP * vals[0] for i in range(m - 1)):
        return False
    for j in range(k):
        mags = np.sort(np.abs(vecs[:, j]))[::-1]
        if len(mags) > 1 and mags[0] - mags[1] < ENTRY_MARGIN:
            return False
    return True
