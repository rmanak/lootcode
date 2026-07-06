"""Input-constraint validator for problem 'group-anagrams'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(strs):
    if not isinstance(strs, list):
        return False
    for s in strs:
        if not isinstance(s, str):
            return False
    return True
