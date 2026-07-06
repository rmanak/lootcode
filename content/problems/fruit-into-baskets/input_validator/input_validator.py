"""Input-constraint validator for problem 'fruit-into-baskets'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(tree):
    if not isinstance(tree, list):
        return False
    if len(tree) < 1 or len(tree) > 40000:
        return False
    n = len(tree)
    for x in tree:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 0 or x >= n:
            return False
    return True
