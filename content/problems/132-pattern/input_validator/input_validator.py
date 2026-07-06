"""Input-constraint validator for problem '132-pattern'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums):
    if not isinstance(nums, list):
        return False
    if len(nums) < 1 or len(nums) > 20000:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
    return True
