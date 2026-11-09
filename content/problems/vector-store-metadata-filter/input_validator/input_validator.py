"""Input-constraint validator for design problem 'vector-store-metadata-filter'.

Hand-written (structural part in the generate_class_validators.py shape).
dim an int in [1, 256]; every vector exactly dim finite numbers with |v| <= 100;
ids non-empty strs of <= 20 chars; metadata and filter dicts of <= 5 str keys
with str/int (not bool) values; topK an int in [1, 50]; at most 3000 calls.
Also enforces the statement's promise about near-ties: in every query, two
matching records whose similarities differ by less than 1e-9 have equal
similarities.
"""
import math

_SIG = {'VectorStore': [('int', 0)], 'upsert': [('string', 0), ('float', 1), ('object', 0)], 'delete': [('string', 0)], 'query': [('float', 1), ('int', 0), ('object', 0)], 'size': []}
_CTOR = 'VectorStore'


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


def _meta_ok(m):
    if not isinstance(m, dict) or len(m) > 5:
        return False
    return all(isinstance(k, str) and isinstance(v, (str, int)) and not isinstance(v, bool) for k, v in m.items())


def _cos(a, b):
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def validate_input(operations, args):
    if not _structure_ok(operations, args) or len(operations) - 1 > 3000:
        return False
    dim = args[0][0]
    if not 1 <= dim <= 256:
        return False
    store = {}
    for op, a in zip(operations[1:], args[1:]):
        if op in ("upsert", "query"):
            v = a[1] if op == "upsert" else a[0]
            if len(v) != dim or not all(math.isfinite(x) and abs(x) <= 100 for x in v):
                return False
            if not _meta_ok(a[2]):
                return False
        if op in ("upsert", "delete") and not (1 <= len(a[0]) <= 20):
            return False
        if op == "upsert":
            store[a[0]] = (a[1], a[2])
        elif op == "delete":
            store.pop(a[0], None)
        elif op == "query":
            if not 1 <= a[1] <= 50:
                return False
            f = a[2]
            s = sorted(_cos(a[0], vec) for vec, m in store.values() if all(k in m and m[k] == x for k, x in f.items()))
            for x, y in zip(s, s[1:]):
                if 0 < y - x < 1e-9:
                    return False
    return True
