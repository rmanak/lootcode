"""Input-constraint validator for problem 'find-all-good-strings'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, s1, s2, evil):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 1 or n > 500:
        return False
    if not isinstance(s1, str):
        return False
    if not isinstance(s2, str):
        return False
    if not isinstance(evil, str):
        return False
    if len(s1) != n:
        return False
    if len(s2) != n:
        return False
    if len(evil) < 1 or len(evil) > 50:
        return False
    if s1 > s2:
        return False
    for c in s1:
        if not ('a' <= c <= 'z'):
            return False
    for c in s2:
        if not ('a' <= c <= 'z'):
            return False
    for c in evil:
        if not ('a' <= c <= 'z'):
            return False
    return True
