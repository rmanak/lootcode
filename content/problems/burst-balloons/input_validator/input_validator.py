"""Input-constraint validator for problem 'burst-balloons'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums):
    if not isinstance(nums, list):
        return False
    if len(nums) < 1 or len(nums) > 300:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 100:
            return False
    return True
