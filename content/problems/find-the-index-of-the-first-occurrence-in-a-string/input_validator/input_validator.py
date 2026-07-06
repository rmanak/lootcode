"""Input-constraint validator for problem 'find-the-index-of-the-first-occurrence-in-a-string'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(haystack, needle):
    if not isinstance(haystack, str) or not isinstance(needle, str):
        return False
    if len(haystack) < 1 or len(haystack) > 10000:
        return False
    if len(needle) < 1 or len(needle) > 10000:
        return False
    for c in haystack:
        if not ('a' <= c <= 'z'):
            return False
    for c in needle:
        if not ('a' <= c <= 'z'):
            return False
    return True
