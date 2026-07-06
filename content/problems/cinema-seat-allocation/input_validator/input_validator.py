"""Input-constraint validator for problem 'cinema-seat-allocation'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(n, reservedSeats):
    if isinstance(n, bool) or not isinstance(n, int):
        return False
    if n < 1 or n > 1000000000:
        return False
    if not isinstance(reservedSeats, list):
        return False
    if len(reservedSeats) < 1 or len(reservedSeats) > min(10 * n, 10000):
        return False
    for row in reservedSeats:
        if not isinstance(row, list):
            return False
        if len(row) != 2:
            return False
        for x in row:
            if isinstance(x, bool) or not isinstance(x, int):
                return False
        if row[0] < 1 or row[0] > n:
            return False
        if row[1] < 1 or row[1] > 10:
            return False
    return True
