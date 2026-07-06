"""Input-constraint validator for problem 'graph-bipartite-check'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(graph):
    if not isinstance(graph, list):
        return False
    if len(graph) < 1 or len(graph) > 1000:
        return False
    n = len(graph)
    for u in range(n):
        if not isinstance(graph[u], list):
            return False
        if len(graph[u]) != len(set(graph[u])):
            return False
        for v in graph[u]:
            if isinstance(v, bool) or not isinstance(v, int):
                return False
            if v < 0 or v >= n:
                return False
            if v == u:
                return False
        for v in graph[u]:
            if u not in graph[v]:
                return False
    return True
