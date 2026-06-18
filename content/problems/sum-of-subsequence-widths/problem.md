The *width* of a sequence is `max - min`. **Return the sum of widths over all
non-empty subsequences of `nums`**, modulo `10^9 + 7`.

**Example**
```
nums = [2,1,3]  ->  6
```
(Subsequence widths: `[1],[2],[3] -> 0`; `[2,1],[2,3] -> 1`; `[1,3] -> 2`;
`[2,1,3] -> 2`; total `6`.)

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^5`.
