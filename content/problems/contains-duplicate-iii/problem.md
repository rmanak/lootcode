**Return `true` if there exist two distinct indices `i` and `j`** with
`abs(nums[i] - nums[j]) <= t` and `abs(i - j) <= k`, else `false`.

**Examples**
```
nums = [1,2,3,1], k = 3, t = 0      ->  true
nums = [1,0,1,1], k = 1, t = 2      ->  true
nums = [1,5,9,1,5,9], k = 2, t = 3  ->  false
```

**Constraints:** `1 <= len(nums) <= 2*10^4`, `0 <= k <= 10^4`, `0 <= t <= 2^31 - 1`.
