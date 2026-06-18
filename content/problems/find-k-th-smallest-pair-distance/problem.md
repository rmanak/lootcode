The distance of a pair `(a, b)` is `|a - b|`. Over all pairs of elements of `nums`,
**return the `k`-th smallest distance** (1-indexed).

**Examples**
```
nums = [1,3,1], k = 1   ->  0
nums = [1,1,1], k = 2   ->  0
nums = [1,6,1], k = 3   ->  5
```

**Constraints:** `2 <= len(nums) <= 10^4`, `0 <= nums[i] <= 10^6`,
`1 <= k <= len(nums)*(len(nums)-1)/2`.
