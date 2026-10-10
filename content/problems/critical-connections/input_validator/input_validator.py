"""Input-constraint validator for problem 'critical-connections'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(n, connections):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 1 or n > 100000:
        return False
    if not isinstance(connections, list):
        return False
    for conn in connections:
        if not isinstance(conn, list):
            return False
        if len(conn) != 2:
            return False
        for x in conn:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 0 or x >= n:
                return False
        if conn[0] == conn[1]:
            return False
    seen = set()
    for conn in connections:
        edge = (min(conn[0], conn[1]), max(conn[0], conn[1]))
        if edge in seen:
            return False
        seen.add(edge)
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - The graph is connected.
#   - No duplicate edges or self-loops.

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

def _simple(edges):
    """No self-loops and no repeated undirected edges."""
    pairs = [frozenset((e[0], e[1])) for e in edges]
    return all(len(p) == 2 for p in pairs) and len(set(pairs)) == len(pairs)


def _stated_promises(n, connections):
    return _simple(connections) and _connected(range(n), connections)


def validate_input(n, connections):
    if not _generated_validate_input(n, connections):
        return False
    try:
        return bool(_stated_promises(n, connections))
    except Exception:  # malformed input the generated check let through
        return False
