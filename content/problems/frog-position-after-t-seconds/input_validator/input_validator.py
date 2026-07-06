"""Input-constraint validator for problem 'frog-position-after-t-seconds'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, edges, t, target):
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
