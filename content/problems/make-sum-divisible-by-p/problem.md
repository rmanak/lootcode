Remove the **smallest contiguous subarray** (possibly empty, but not the whole array)
so that the sum of the remaining elements is divisible by `p`. **Return the length of
that subarray, or `-1` if impossible.**

**Examples**
```
nums = [3,1,4,2], p = 6  ->  1
nums = [6,3,5,2], p = 9  ->  2
nums = [1,2,3], p = 3    ->  0
nums = [1,2,3], p = 7    ->  -1
```

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^9`, `1 <= p <= 10^9`.
