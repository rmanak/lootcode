"""Input-constraint validator for problem 'coin-change-ways'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(amount, coins):
    if isinstance(amount, bool) or not isinstance(amount, int):
        return False
    if amount < 0 or amount > 5000:
        return False
    if not isinstance(coins, list):
        return False
    if len(coins) < 1 or len(coins) > 300:
        return False
    for x in coins:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 5000:
            return False
    return True
