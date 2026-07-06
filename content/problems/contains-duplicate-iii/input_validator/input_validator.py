"""Input-constraint validator for problem 'contains-duplicate-iii'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums, k, t):
    if not isinstance(nums, list):
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    if isinstance(t, bool) or not isinstance(t, int):
        return False
    if len(nums) < 1 or len(nums) > 20000:
        return False
    if k < 0 or k > 10000:
        return False
    if t < 0 or t > 2147483647:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
    return True
