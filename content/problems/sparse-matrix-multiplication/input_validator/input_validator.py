"""Input-constraint validator for problem 'sparse-matrix-multiplication'.

Hand-written. mat1 is m x k and mat2 is k x n with 1 <= m, k, n <= 300;
every entry an int (not a bool) in [-100, 100].
"""


def _matrix(M):
    if not isinstance(M, list) or not 1 <= len(M) <= 300 or not isinstance(M[0], list):
        return None
    w = len(M[0])
    if not 1 <= w <= 300:
        return None
    for r in M:
        if not isinstance(r, list) or len(r) != w:
            return None
        if not all(isinstance(v, int) and not isinstance(v, bool) and -100 <= v <= 100 for v in r):
            return None
    return len(M), w


def validate_input(mat1, mat2):
    a, b = _matrix(mat1), _matrix(mat2)
    return a is not None and b is not None and a[1] == b[0]
