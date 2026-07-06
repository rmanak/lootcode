"""Input-constraint validator for problem 'distinct-echo-substrings'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(text):
    if not isinstance(text, str):
        return False
    if len(text) < 1 or len(text) > 2000:
        return False
    for c in text:
        if not ('a' <= c <= 'z'):
            return False
    return True
