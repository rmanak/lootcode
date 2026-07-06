"""Input-constraint validator for problem 'image-overlap'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(img1, img2):
    if not isinstance(img1, list) or not isinstance(img2, list):
        return False
    n = len(img1)
    if len(img2) != n:
        return False
    if n < 1 or n > 30:
        return False
    for row in img1:
        if not isinstance(row, list) or len(row) != n:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1:
                return False
    for row in img2:
        if not isinstance(row, list) or len(row) != n:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1:
                return False
    return True
