"""Input-constraint validator for problem 'gas-station'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(gas, cost):
    if not isinstance(gas, list) or not isinstance(cost, list):
        return False
    if len(gas) != len(cost):
        return False
    if len(gas) < 1 or len(gas) > 100000:
        return False
    for x in gas:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0:
            return False
    for x in cost:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0:
            return False
    return True
