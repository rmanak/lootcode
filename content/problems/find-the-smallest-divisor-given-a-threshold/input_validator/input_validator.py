"""Input-constraint validator for problem 'find-the-smallest-divisor-given-a-threshold'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums, threshold):
    if not isinstance(nums, list):
        return False
    if isinstance(threshold, bool) or not isinstance(threshold, int):
        return False
    if len(nums) < 1 or len(nums) > 50000:
        return False
    if threshold < len(nums) or threshold > 1000000:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 1000000:
            return False
    return True
