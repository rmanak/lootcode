"""Input-constraint validator for problem 'binary-search'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums, target):
    if not isinstance(nums, list):
        return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
    for i in range(len(nums) - 1):
        if nums[i] >= nums[i + 1]:
            return False
    return True
