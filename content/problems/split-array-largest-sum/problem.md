Split `nums` into `m` non-empty contiguous subarrays. **Return the minimum possible
value of the largest subarray sum** over all such splits.

**Examples**
```
nums = [7,2,5,10,8], m = 2  ->  18
nums = [1,2,3,4,5], m = 2   ->  9
nums = [1,4,4], m = 3       ->  4
```

**Constraints:** `1 <= len(nums) <= 1000`, `1 <= m <= min(50, len(nums))`,
`0 <= nums[i]`.
