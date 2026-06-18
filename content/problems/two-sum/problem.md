# Two Sum

Given an array of integers `nums` and an integer `target`, return the **indices
of the two numbers** that add up to `target`.

You may assume that each input has **exactly one solution**, and you may not use
the same element twice. You can return the answer in any order.

## Constraints

- `2 <= nums.length <= 10^4`
- `-10^9 <= nums[i] <= 10^9`
- `-10^9 <= target <= 10^9`
- Exactly one valid answer exists.

## Examples

**Example 1**
```
Input:  nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
Explanation: nums[0] + nums[1] == 9.
```

**Example 2**
```
Input:  nums = [3, 2, 4], target = 6
Output: [1, 2]
```

**Example 3**
```
Input:  nums = [3, 3], target = 6
Output: [0, 1]
```

> The answer may be returned in either order — the judge compares the pair as an
> unordered set (see `compare: "unordered"` in `meta.json`).
