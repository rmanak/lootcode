"""Input-constraint validator for problem 'find-the-shortest-superstring'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(words):
    if not isinstance(words, list):
        return False
    if len(words) < 1 or len(words) > 12:
        return False
    for w in words:
        if not isinstance(w, str):
            return False
        if len(w) < 1 or len(w) > 20:
            return False
        if not w.isalpha() or not w.islower():
            return False
    return True
