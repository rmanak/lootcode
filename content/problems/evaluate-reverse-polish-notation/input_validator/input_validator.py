"""Input-constraint validator for problem 'evaluate-reverse-polish-notation'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(tokens):
    if not isinstance(tokens, list):
        return False
    if len(tokens) < 1 or len(tokens) > 10000:
        return False
    for t in tokens:
        if not isinstance(t, str):
            return False
        if t in ('+', '-', '*', '/'):
            continue
        try:
            val = int(t)
        except ValueError:
            return False
        if val < -20000 or val > 20000:
            return False
    return True
