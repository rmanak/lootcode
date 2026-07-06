"""Input-constraint validator for problem 'best-time-to-buy-and-sell-stock-iv'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(prices, k):
    if not isinstance(prices, list):
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if len(prices) < 0 or len(prices) > 1000:
        return False
    if k < 0 or k > 100:
        return False
    for x in prices:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1000:
            return False
    return True
