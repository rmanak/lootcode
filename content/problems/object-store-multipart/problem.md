A multipart upload provides `parts`, each `[partNumber, bytes]`. Return a two-element
list `[complete, totalBytes]` where `complete` is `true` only if every part number
`1..expected` is present, and `totalBytes` is the sum of all uploaded part sizes.

## Constraints
- `0 <= len(parts) <= 2*10^5`, `1 <= expected`
- part numbers are positive; sizes fit in a signed 64-bit integer

## Examples
Input: `parts = [[1,5],[3,7],[2,4]], expected = 3`
Output: `[true,16]`
Explanation: Parts 1, 2, 3 are present; total `5+7+4 = 16`.

Input: `parts = [[1,5],[3,7]], expected = 3`
Output: `[false,12]`
Explanation: Part 2 is missing; total bytes are still `12`.
