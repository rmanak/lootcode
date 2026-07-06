"""Input-constraint validator for problem '24-game'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(cards):
    if not isinstance(cards, list):
        return False
    if len(cards) != 4:
        return False
    for x in cards:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 9:
            return False
    return True
