"""Input-constraint validator for problem 'contains-nearby-almost-duplicate'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums, indexDiff, valueDiff):
    if not isinstance(nums, list):
        return False
    if len(nums) < 1 or len(nums) > 100000:
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < -1000000000 or x > 1000000000:
            return False
    if isinstance(indexDiff, bool) or not isinstance(indexDiff, int):
        return False
    if indexDiff < 0:
        return False
    if isinstance(valueDiff, bool) or not isinstance(valueDiff, int):
        return False
    if valueDiff < 0:
        return False
    return True
