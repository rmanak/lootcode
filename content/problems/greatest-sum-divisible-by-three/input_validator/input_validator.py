"""Input-constraint validator for problem 'greatest-sum-divisible-by-three'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums):
    if not isinstance(nums, list):
        return False
    if len(nums) < 1 or len(nums) > 40000:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 10000:
            return False
    return True
