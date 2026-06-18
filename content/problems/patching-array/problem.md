`nums` is a sorted array of positive integers. **Return the minimum number of
elements to add** so that every integer in `[1, n]` can be formed as a sum of some
subset of the (patched) array.

**Examples**
```
nums = [1,3], n = 6      ->  1
nums = [1,5,10], n = 20  ->  2
nums = [1,2,2], n = 5    ->  0
```

**Constraints:** `0 <= len(nums) <= 1000`, `1 <= n <= 2^31 - 1`.
