Each employee has a list of non-overlapping working intervals `[start, end]`,
sorted by start. Return **the finite intervals of time, sorted, during which every
employee is free** (the common gaps between the union of all working intervals).
Return them as a list of `[start, end]`.

## Constraints
- `1 <= number of employees <= 100`; each has `1` to `100` intervals.
- `0 <= start < end <= 10^9`.

## Examples
Input: `schedule = [[[1,2],[5,6]],[[1,3]],[[4,10]]]`
Output: `[[3,4]]`
Explanation: union of work is `[1,3],[4,10]`; the only common gap is `[3,4]`.

Input: `schedule = [[[1,3],[6,7]],[[2,4]],[[2,5],[9,12]]]`
Output: `[[5,6],[7,9]]`

Input: `schedule = [[[1,4]],[[2,3]]]`
Output: `[]`
