"""Input-constraint validator for problem 'count-of-smaller-numbers-after-self'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums):
    if not isinstance(nums, list):
        return False
    if len(nums) < 0 or len(nums) > 100000:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < -2147483648 or x > 2147483647:
            return False
    return True
