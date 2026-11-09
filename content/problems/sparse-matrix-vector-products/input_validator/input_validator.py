"""Input-constraint validator for design problem 'sparse-matrix-vector-products'.

Hand-written (structural part in the generate_class_validators.py shape).
rows, cols ints in [1, 1e9]; at most 1e5 initial entries [i, j, v] with
in-range distinct positions and v a non-zero int in [-1e4, 1e4]; set takes
an in-range position and a value in [-1e4, 1e4]; each vector is <= 1e4
[index, value] pairs with strictly increasing in-range indices (cols for
multiplyVector, rows for vectorMultiply) and non-zero values in [-1e4, 1e4];
at most 5000 calls.
"""

_SIG = {'SparseMatrix': [('int', 0), ('int', 0), ('int', 2)], 'set': [('int', 0), ('int', 0), ('int', 0)], 'multiplyVector': [('int', 2)], 'vectorMultiply': [('int', 2)]}
_CTOR = 'SparseMatrix'


def _scalar_ok(v, base):
    if base == "int":
        return isinstance(v, int) and not isinstance(v, bool)
    if base in ("float", "num"):
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if base == "bool":
        return isinstance(v, bool)
    if base in ("string", "str", "char"):
        return isinstance(v, str)
    return True


def _type_ok(v, base, dims):
    if dims == 0:
        return _scalar_ok(v, base)
    if not isinstance(v, list):
        return False
    return all(_type_ok(e, base, dims - 1) for e in v)


def _structure_ok(operations, args):
    if not isinstance(operations, list) or not isinstance(args, list):
        return False
    if len(operations) != len(args) or not operations or operations[0] != _CTOR:
        return False
    for i, (op, a) in enumerate(zip(operations, args)):
        if op not in _SIG or (op == _CTOR) != (i == 0):
            return False
        if not isinstance(a, list) or len(a) != len(_SIG[op]):
            return False
        if not all(_type_ok(v, b, d) for v, (b, d) in zip(a, _SIG[op])):
            return False
    return True


def _vec(v, dim):
    if len(v) > 10000:
        return False
    last = -1
    for p in v:
        if len(p) != 2 or not (last < p[0] < dim) or p[1] == 0 or not -10**4 <= p[1] <= 10**4:
            return False
        last = p[0]
    return True


def validate_input(operations, args):
    if not _structure_ok(operations, args) or len(operations) - 1 > 5000:
        return False
    R, C, E = args[0]
    if not (1 <= R <= 10**9 and 1 <= C <= 10**9) or len(E) > 100000:
        return False
    seen = set()
    for e in E:
        if len(e) != 3 or not (0 <= e[0] < R and 0 <= e[1] < C) or e[2] == 0 or not -10**4 <= e[2] <= 10**4:
            return False
        if (e[0], e[1]) in seen:
            return False
        seen.add((e[0], e[1]))
    for op, a in zip(operations[1:], args[1:]):
        if op == "set" and not (0 <= a[0] < R and 0 <= a[1] < C and -10**4 <= a[2] <= 10**4):
            return False
        if op == "multiplyVector" and not _vec(a[0], C):
            return False
        if op == "vectorMultiply" and not _vec(a[0], R):
            return False
    return True
