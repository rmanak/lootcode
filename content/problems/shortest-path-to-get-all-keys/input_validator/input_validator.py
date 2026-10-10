"""Input-constraint validator for problem 'shortest-path-to-get-all-keys'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-written: enforces exactly one "@", and that the keys are
the first k lowercase letters (1 <= k <= 6), each exactly once, with at most one lock
per key and no lock without its key. The canonical relies on this (it targets the
mask of the first k letters).
The generated version skipped this as a "semantic guarantee", which let the
retired test generator bake in a malformed hidden case. Do not regenerate.
"""
_ALLOWED = set(".#@abcdefABCDEF")
_KEYS = "abcdef"


def validate_input(grid):
    if not isinstance(grid, list) or not grid:
        return False
    if not (1 <= len(grid) <= 30):
        return False
    if not isinstance(grid[0], str):
        return False
    cols = len(grid[0])
    if not (1 <= cols <= 30):
        return False
    cells = []
    for row in grid:
        if not isinstance(row, str) or len(row) != cols:
            return False
        if not set(row) <= _ALLOWED:
            return False
        cells.extend(row)
    if cells.count("@") != 1:
        return False
    keys = sorted(c for c in cells if c.islower())
    locks = [c for c in cells if c.isupper()]
    k = len(keys)
    if not (1 <= k <= 6) or "".join(keys) != _KEYS[:k]:
        return False
    if len(set(locks)) != len(locks):
        return False
    return all(c.lower() in keys for c in locks)
