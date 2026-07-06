"""Input-constraint validator for problem 'find-k-th-smallest-pair-distance'.

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
    if len(nums) < 2 or len(nums) > 10000:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int) or x < 0 or x > 1000000:
            return False
    max_k = len(nums) * (len(nums) - 1) // 2
    if k < 1 or k > max_k:
        return False
    return True
