"""Input-constraint validator for problem 'delete-columns-to-make-sorted-ii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(strs):
    if not isinstance(strs, list):
        return False
    if len(strs) < 1 or len(strs) > 100:
        return False
    first_len = None
    for s in strs:
        if not isinstance(s, str):
            return False
        slen = len(s)
        if slen < 1 or slen > 100:
            return False
        if first_len is None:
            first_len = slen
        elif slen != first_len:
            return False
    return True
