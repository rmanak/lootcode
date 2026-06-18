A subarray is *nice* if it contains exactly `k` odd numbers. **Return the number of
nice subarrays.**

**Examples**
```
nums = [1,1,2,1,1], k = 3              ->  2
nums = [2,4,6], k = 1                  ->  0
nums = [2,2,2,1,2,2,1,2,2,2], k = 2    ->  16
```

**Constraints:** `1 <= len(nums) <= 5*10^4`, `1 <= nums[i] <= 10^5`,
`1 <= k <= len(nums)`.
