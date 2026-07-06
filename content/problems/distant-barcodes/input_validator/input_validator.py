"""Input-constraint validator for problem 'distant-barcodes'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(barcodes):
    if not isinstance(barcodes, list):
        return False
    if len(barcodes) < 1 or len(barcodes) > 10000:
        return False
    for x in barcodes:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 10000:
            return False
    return True
