"""Input-constraint validator for problem 'frog-position-after-t-seconds'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(n, edges, t, target):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if not isinstance(edges, list):
        return False
    if isinstance(t, bool) or not isinstance(t, int):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if n < 1 or n > 100:
        return False
    if len(edges) != n - 1:
        return False
    if t < 1 or t > 50:
        return False
    if target < 1 or target > n:
        return False
    for edge in edges:
        if not isinstance(edge, list):
            return False
        if len(edge) != 2:
            return False
        for x in edge:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 1 or x > n:
                return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - The edges form an undirected tree on vertices `1..n`.

def _connected(nodes, edges):
    """True if the undirected graph on ``nodes`` (an iterable of labels) is connected."""
    nodes = list(nodes)
    parent = {v: v for v in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for e in edges:
        parent[find(e[0])] = find(e[1])
    return len({find(v) for v in nodes}) <= 1


def _stated_promises(n, edges, t, target):
    return len(edges) == n - 1 and _connected(range(1, n + 1), edges)


def validate_input(n, edges, t, target):
    if not _generated_validate_input(n, edges, t, target):
        return False
    try:
        return bool(_stated_promises(n, edges, t, target))
    except Exception:  # malformed input the generated check let through
        return False
