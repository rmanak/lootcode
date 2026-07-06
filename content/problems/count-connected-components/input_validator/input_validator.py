"""Input-constraint validator for problem 'count-connected-components'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, edges):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 1 or n > 2000:
        return False
    if not isinstance(edges, list):
        return False
    max_edges = n * (n - 1) // 2
    if len(edges) < 0 or len(edges) > max_edges:
        return False
    seen = set()
    for edge in edges:
        if not isinstance(edge, list):
            return False
        if len(edge) != 2:
            return False
        u, v = edge[0], edge[1]
        if isinstance(u, bool) or not isinstance(u, int):
            return False
        if isinstance(v, bool) or not isinstance(v, int):
            return False
        if u < 0 or u >= n or v < 0 or v >= n:
            return False
        if u == v:
            return False
        key = (min(u, v), max(u, v))
        if key in seen:
            return False
        seen.add(key)
    return True
