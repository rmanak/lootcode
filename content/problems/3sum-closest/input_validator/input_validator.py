"""Input-constraint validator for problem '3sum-closest'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums, target):
    if not isinstance(nums, list):
        return False
    if len(nums) < 3 or len(nums) > 500:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int) or x < -1000 or x > 1000:
            return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if target < -1000 or target > 1000:
        return False
    return True
