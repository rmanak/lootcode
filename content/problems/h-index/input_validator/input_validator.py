"""Input-constraint validator for problem 'h-index'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(citations):
    if not isinstance(citations, list):
        return False
    if len(citations) < 0 or len(citations) > 5000:
        return False
    for x in citations:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1000:
            return False
    return True
