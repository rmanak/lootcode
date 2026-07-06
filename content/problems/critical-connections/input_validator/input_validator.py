"""Input-constraint validator for problem 'critical-connections'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, connections):
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
