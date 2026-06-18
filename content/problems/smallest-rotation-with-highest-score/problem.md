Rotate `nums` by a non-negative integer `K`, producing
`nums[K], nums[K+1], ..., nums[n-1], nums[0], ..., nums[K-1]`. After rotating, any
entry that is **less than or equal to its new index** earns 1 point.

Over all rotations, return the index `K` that yields the highest score. If several
`K` tie, return the **smallest** such `K`.

**Examples**
```
nums = [2,3,1,4,0]  ->  3   (rotation by 3 scores 4, the maximum)
nums = [1,3,0,2,4]  ->  0   (every rotation scores 3, so pick the smallest K)
```

**Constraints:** `1 <= len(nums) <= 2000`, `0 <= nums[i] <= len(nums)`.
