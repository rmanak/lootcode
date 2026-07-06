"""Input-constraint validator for problem 'constrained-subsequence-sum'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums, k):
    if not isinstance(nums, list):
        return False
    if isinstance(k, bool) or not isinstance(k, int):
        return False
    n = len(nums)
    if n < 1 or n > 100000:
        return False
    if k < 1 or k > n:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int) or x < -10000 or x > 10000:
            return False
    return True
