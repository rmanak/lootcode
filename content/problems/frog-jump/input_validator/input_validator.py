"""Input-constraint validator for problem 'frog-jump'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(stones):
    if not isinstance(stones, list):
        return False
    if len(stones) < 2 or len(stones) > 2000:
        return False
    for x in stones:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
    if stones[0] != 0:
        return False
    for i in range(1, len(stones)):
        if stones[i] <= stones[i - 1]:
            return False
    return True
