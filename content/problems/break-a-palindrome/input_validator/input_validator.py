"""Input-constraint validator for problem 'break-a-palindrome'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(palindrome):
    if not isinstance(palindrome, str):
        return False
    if len(palindrome) < 1 or len(palindrome) > 1000:
        return False
    for c in palindrome:
        if not ('a' <= c <= 'z'):
            return False
    return True
