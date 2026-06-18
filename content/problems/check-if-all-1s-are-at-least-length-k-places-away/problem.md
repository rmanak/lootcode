`nums` is an array of `0`s and `1`s. **Return `true` if every pair of consecutive
`1`s is separated by at least `k` `0`s** (i.e. their index difference is `> k`),
otherwise `false`.

**Examples**
```
nums = [1,0,0,0,1,0,0,1], k = 2  ->  true
nums = [1,0,0,1,0,1], k = 2      ->  false
nums = [1,1,1,1,1], k = 0        ->  true
```

**Constraints:** `1 <= len(nums) <= 10^5`, `0 <= k <= len(nums)`, `nums[i]` in
`{0,1}`.
