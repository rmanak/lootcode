"""Input-constraint validator for problem 'all-paths-from-source-to-target'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(graph):
    if not isinstance(graph, list):
        return False
    n = len(graph)
    if n < 2 or n > 15:
        return False
    for row in graph:
        if not isinstance(row, list):
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 0 or x >= n:
                return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - The graph is acyclic.

def _acyclic(nodes, edges):
    """Kahn's algorithm over directed ``edges`` (u -> v)."""
    nodes = list(nodes)
    indeg = {v: 0 for v in nodes}
    out = {v: [] for v in nodes}
    for e in edges:
        out[e[0]].append(e[1])
        indeg[e[1]] += 1
    ready = [v for v in nodes if indeg[v] == 0]
    seen = 0
    while ready:
        v = ready.pop()
        seen += 1
        for w in out[v]:
            indeg[w] -= 1
            if indeg[w] == 0:
                ready.append(w)
    return seen == len(nodes)


def _stated_promises(graph):
    n = len(graph)
    return _acyclic(range(n), [(u, v) for u in range(n) for v in graph[u]])


def validate_input(graph):
    if not _generated_validate_input(graph):
        return False
    try:
        return bool(_stated_promises(graph))
    except Exception:  # malformed input the generated check let through
        return False
