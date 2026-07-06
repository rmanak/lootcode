"""Input-constraint validator for problem 'delete-columns-to-make-sorted-iii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(A):
    if not isinstance(A, list):
        return False
    if len(A) < 1 or len(A) > 100:
        return False
        
    first_len = None
    for s in A:
        if not isinstance(s, str):
            return False
        if len(s) < 1 or len(s) > 100:
            return False
        if first_len is None:
            first_len = len(s)
        elif len(s) != first_len:
            return False
        for c in s:
            if not ('a' <= c <= 'z'):
                return False
    return True
