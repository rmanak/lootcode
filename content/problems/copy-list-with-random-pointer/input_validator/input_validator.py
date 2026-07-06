"""Input-constraint validator for problem 'copy-list-with-random-pointer'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(head):
    if not isinstance(head, list):
        return False
    n = len(head)
    if n < 0 or n > 1000:
        return False
    for pair in head:
        if not isinstance(pair, list):
            return False
        if len(pair) != 2:
            return False
        val, random_index = pair
        if isinstance(val, bool) or not isinstance(val, int):
            return False
        if val < -10000 or val > 10000:
            return False
        if random_index is not None:
            if isinstance(random_index, bool) or not isinstance(random_index, int):
                return False
            if random_index < 0 or random_index >= n:
                return False
    return True
