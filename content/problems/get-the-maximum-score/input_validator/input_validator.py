"""Input-constraint validator for problem 'get-the-maximum-score'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(nums1, nums2):
    if not isinstance(nums1, list) or not isinstance(nums2, list):
        return False
    if len(nums1) < 1 or len(nums1) > 100000:
        return False
    if len(nums2) < 1 or len(nums2) > 100000:
        return False
        
    for x in nums1:
        if not isinstance(x, int) or isinstance(x, bool) or x < 1 or x > 10000000:
            return False
    for x in nums2:
        if not isinstance(x, int) or isinstance(x, bool) or x < 1 or x > 10000000:
            return False
            
    for i in range(1, len(nums1)):
        if nums1[i] <= nums1[i-1]:
            return False
    for i in range(1, len(nums2)):
        if nums2[i] <= nums2[i-1]:
            return False
            
    return True
