"""Input-constraint validator for problem 'bootstrap-and-jackknife'.

Hand-written. groups: n ints (4 <= n <= 2e4) each 0 or 1, both groups with
>= 2 rows; values: n finite numbers with |v| <= 1e9; resample0/resample1:
B rows each (1 <= B <= 2000, B*n <= 2e5) of n0 / n1 ints in [0, n0) /
[0, n1); alpha a number strictly between 0 and 1.
"""
import math


def _idx_rows(R, B, k):
    if not isinstance(R, list) or len(R) != B:
        return False
    for row in R:
        if not isinstance(row, list) or len(row) != k:
            return False
        if not all(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < k for i in row):
            return False
    return True


def validate_input(groups, values, resample0, resample1, alpha):
    if not isinstance(groups, list) or not isinstance(values, list):
        return False
    n = len(groups)
    if not 4 <= n <= 20000 or len(values) != n:
        return False
    if not all(isinstance(x, int) and not isinstance(x, bool) and x in (0, 1) for x in groups):
        return False
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and abs(x) <= 1e9
               for x in values):
        return False
    n1 = sum(groups); n0 = n - n1
    if n0 < 2 or n1 < 2:
        return False
    if not isinstance(resample0, list):
        return False
    B = len(resample0)
    if not 1 <= B <= 2000 or B * n > 200000:
        return False
    if not _idx_rows(resample0, B, n0) or not _idx_rows(resample1, B, n1):
        return False
    return isinstance(alpha, (int, float)) and not isinstance(alpha, bool) and 0 < alpha < 1
