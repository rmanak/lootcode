"""Input-constraint validator for problem 'coin-change'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(coins, amount):
    if not isinstance(coins, list):
        return False
    if isinstance(amount, bool) or not isinstance(amount, int):
        return False
    if len(coins) < 1:
        return False
    if amount < 0:
        return False
    for x in coins:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1:
            return False
    return True
