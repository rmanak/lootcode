**Return the maximum sum of a non-empty subsequence** of `nums` such that any two
consecutive chosen elements are at most `k` indices apart (if `nums[i]` and
`nums[j]` are consecutive in the subsequence with `i < j`, then `j - i <= k`).

**Examples**
```
nums = [10,2,-10,5,20], k = 2  ->  37   ([10,2,5,20])
nums = [-1,-2,-3], k = 1       ->  -1
nums = [10,-2,-10,-5,20], k = 2 ->  23   ([10,-2,-5,20])
```

**Constraints:** `1 <= k <= len(nums) <= 10^5`, `-10^4 <= nums[i] <= 10^4`.
