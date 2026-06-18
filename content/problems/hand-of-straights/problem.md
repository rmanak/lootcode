Determine whether the cards in `hand` can be partitioned into groups of exactly
`groupSize` cards where each group is `groupSize` **consecutive** values.

## Constraints
- `1 <= len(hand) <= 10^5`
- `1 <= hand[i] <= 10^9`
- `1 <= groupSize <= len(hand)`

## Examples
Input: `hand = [1,2,3,6,2,3,4,7,8], groupSize = 3`
Output: `true`
Explanation: Groups `[1,2,3]`, `[2,3,4]`, `[6,7,8]`.

Input: `hand = [1,2,3,4,5], groupSize = 4`
Output: `false`
Explanation: Five cards cannot split into groups of four.
