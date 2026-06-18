Given an initial array `nums`, replay `operations` and return the list of results.
Operations are `["query", l, r]` returning the sum `nums[l] + ... + nums[r]`
(inclusive), and `["update", i, val]` setting `nums[i] = val` (returns `null`).

## Constraints
- `1 <= len(nums) <= 3*10^4`, `1 <= len(operations) <= 3*10^4`
- `0 <= l <= r < len(nums)`, `0 <= i < len(nums)`

## Examples
Input: `nums = [1,3,5], operations = [["query",0,2],["update",1,2],["query",0,2]]`
Output: `[9,null,8]`
Explanation: The initial sum is `9`; after `nums[1]=2` the sum is `1+2+5=8`.

Input: `nums = [2], operations = [["query",0,0]]`
Output: `[2]`
Explanation: The only element is `2`.
