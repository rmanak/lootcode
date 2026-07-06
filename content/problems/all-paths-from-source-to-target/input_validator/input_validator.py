"""Input-constraint validator for problem 'all-paths-from-source-to-target'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(graph):
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
