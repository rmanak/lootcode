"""Input-constraint validator for problem 'bus-routes'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(routes, source, target):
    if not isinstance(routes, list):
        return False
    if isinstance(source, bool) or not isinstance(source, int):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if len(routes) < 1 or len(routes) > 500:
        return False
    if source < 0 or source >= 1000000:
        return False
    if target < 0 or target >= 1000000:
        return False
    for route in routes:
        if not isinstance(route, list):
            return False
        for x in route:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
    return True
