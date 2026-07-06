"""Input-constraint validator for problem 'find-duplicate-number'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums):
    if not isinstance(nums, list):
        return False
    if len(nums) < 2:
        return False
    n = len(nums) - 1
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > n:
            return False
    seen = {}
    for x in nums:
        seen[x] = seen.get(x, 0) + 1
    duplicated = sum(1 for c in seen.values() if c > 1)
    if duplicated != 1:
        return False
    return True
