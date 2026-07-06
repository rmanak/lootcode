"""Input-constraint validator for problem 'cat-and-mouse'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(graph):
    if not isinstance(graph, list):
        return False
    if len(graph) < 3 or len(graph) > 50:
        return False
    for row in graph:
        if not isinstance(row, list):
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 0 or x >= len(graph):
                return False
    if len(graph[1]) < 1:
        return False
    has_nonzero = False
    for x in graph[2]:
        if x != 0:
            has_nonzero = True
            break
    if not has_nonzero:
        return False
    return True
