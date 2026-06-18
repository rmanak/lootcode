`processed` lists the offsets that have been handled for one partition (unsorted, and
possibly containing duplicates). Return the largest offset `m` such that **every**
offset from `0` through `m` has been processed, or `-1` if offset `0` is missing.

## Constraints
- `1 <= len(processed) <= 2*10^5`
- `0 <= processed[i]`

## Examples
Input: `processed = [0,2,1,5]`
Output: `2`
Explanation: `0,1,2` are contiguous; `3` is missing.

Input: `processed = [1,2]`
Output: `-1`
Explanation: Offset `0` was never processed.
