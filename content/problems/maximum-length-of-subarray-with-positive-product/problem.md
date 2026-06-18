Given an array `nums`, **return the maximum length of a contiguous subarray whose
product is strictly positive**. A subarray containing a `0` has product `0` (not
positive), so it must avoid zeros.

**Examples**
```
nums = [1,-2,-3,4]      ->  4    (whole array, product 24)
nums = [0,1,-2,-3,-4]   ->  3    ([1,-2,-3])
nums = [-1,-2,-3,0,1]   ->  2
```

**Constraints:** `1 <= len(nums) <= 10^5`, `-10^9 <= nums[i] <= 10^9`.
