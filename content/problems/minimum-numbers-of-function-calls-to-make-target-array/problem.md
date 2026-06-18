Start from an all-zero array the same length as `nums`. Two operations are allowed:
add `1` to any single element, or double **every** element. **Return the minimum
number of operations to turn the zero array into `nums`.**

**Examples**
```
nums = [1,5]       ->  5
nums = [2,2]       ->  3
nums = [4,2,5]     ->  6
nums = [2,4,8,16]  ->  8
```

**Constraints:** `1 <= len(nums) <= 10^5`, `0 <= nums[i] <= 10^9`.
