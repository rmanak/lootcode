"""Input-constraint validator for problem 'count-the-repetitions'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(s1, n1, s2, n2):
    if not isinstance(s1, str):
        return False
    if len(s1) < 1 or len(s1) > 100:
        return False
    if not isinstance(s2, str):
        return False
    if len(s2) < 1 or len(s2) > 100:
        return False
    if isinstance(n1, bool) or not isinstance(n1, int):
        return False
    if n1 < 0 or n1 > 1000000:
        return False
    if isinstance(n2, bool) or not isinstance(n2, int):
        return False
    if n2 < 1 or n2 > 1000000:
        return False
    return True
