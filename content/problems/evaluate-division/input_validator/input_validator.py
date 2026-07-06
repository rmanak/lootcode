"""Input-constraint validator for problem 'evaluate-division'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(equations, values, queries):
    if not isinstance(equations, list):
        return False
    if len(equations) < 1 or len(equations) > 20:
        return False
    if not isinstance(values, list):
        return False
    if len(values) != len(equations):
        return False
    if not isinstance(queries, list):
        return False

    for eq in equations:
        if not isinstance(eq, list) or len(eq) != 2:
            return False
        for var in eq:
            if not isinstance(var, str):
                return False
            if not var.islower() or not var.isalpha():
                return False

    for v in values:
        if isinstance(v, bool) or not isinstance(v, float):
            return False
        if v <= 0:
            return False

    for q in queries:
        if not isinstance(q, list) or len(q) != 2:
            return False
        for var in q:
            if not isinstance(var, str):
                return False
            if not var.islower() or not var.isalpha():
                return False

    return True
