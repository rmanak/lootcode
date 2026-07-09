"""Input-constraint validator for problem 'search-in-rotated-sorted-array-ii'.

`validate_input(...)` returns True iff its arguments satisfy the input constraints
stated in the problem. The rotated-sorted check ensures the array has at most one
descent point (wrapping around), which is the structural property of a rotated
non-decreasing sorted array that may contain duplicates.
"""

def _is_rotated_sorted(nums):
    """Check if nums is a rotated non-decreasing sorted array (may contain duplicates)."""
    descents = 0
    n = len(nums)
    for i in range(n):
        if nums[i] > nums[(i + 1) % n]:
            descents += 1
            if descents > 1:
                return False
    return True

def validate_input(nums, target):
    if not isinstance(nums, list):
        return False
    if not (1 <= len(nums) <= 5000):
        return False
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if not (-10**4 <= x <= 10**4):
            return False
    if isinstance(target, bool) or not isinstance(target, int):
        return False
    if not (-10**4 <= target <= 10**4):
        return False
    if not _is_rotated_sorted(nums):
        return False
    return True
