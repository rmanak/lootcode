"""Input-constraint validator for problem 'brick-wall'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(wall):
    if not isinstance(wall, list):
        return False
    if len(wall) < 1 or len(wall) > 10000:
        return False

    total_bricks = 0
    row_sum = None

    for row in wall:
        if not isinstance(row, list):
            return False
        if len(row) < 1 or len(row) > 10000:
            return False
        total_bricks += len(row)

        current_sum = 0
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
            if x < 1:
                return False
            current_sum += x

        if row_sum is None:
            row_sum = current_sum
        elif row_sum != current_sum:
            return False

    if total_bricks > 20000:
        return False

    return True
