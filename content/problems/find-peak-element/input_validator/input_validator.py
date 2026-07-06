"""Input-constraint validator for problem 'find-peak-element'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums):
    if not isinstance(nums, list):
        return False
    if len(nums) < 1 or len(nums) > 100000:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            return False

    n = len(nums)
    if n == 1:
        return True

    peak = 0
    for i in range(1, n):
        if nums[i] > nums[i - 1]:
            peak = i
        else:
            break

    for i in range(1, peak + 1):
        if nums[i] <= nums[i - 1]:
            return False

    for i in range(peak + 1, n):
        if nums[i] >= nums[i - 1]:
            return False

    return True
