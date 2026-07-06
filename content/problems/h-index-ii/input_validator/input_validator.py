"""Input-constraint validator for problem 'h-index-ii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(citations):
    if not isinstance(citations, list):
        return False
    if len(citations) > 100000:
        return False
    for i in range(len(citations)):
        x = citations[i]
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < 0 or x > 1000:
            return False
        if i > 0 and citations[i-1] > x:
            return False
    return True
