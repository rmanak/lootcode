An array sorted in ascending order is rotated at some unknown pivot (for example
`[0,0,1,2,2,5,6]` might become `[2,5,6,0,0,1,2]`). The array **may contain
duplicates**. Given the rotated array `nums` and a `target`, **return `true` if
`target` is present**, otherwise `false`.

**Examples**
```
nums = [2,5,6,0,0,1,2], target = 0  ->  true
nums = [2,5,6,0,0,1,2], target = 3  ->  false
```

**Constraints:** `1 <= len(nums) <= 5000`, `-10^4 <= nums[i], target <= 10^4`.
