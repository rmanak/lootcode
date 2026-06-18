Each `envelopes[i] = [width, height]`. One envelope fits inside another only if
**both** its width and height are strictly smaller. Return the maximum number of
envelopes you can nest (like Russian dolls).

## Constraints
- `1 <= len(envelopes) <= 10^5`
- `1 <= width, height <= 10^5`

## Examples
Input: `envelopes = [[5,4],[6,4],[6,7],[2,3]]`
Output: `3`
Explanation: `[2,3] -> [5,4] -> [6,7]`.

Input: `envelopes = [[1,1],[1,1],[1,1]]`
Output: `1`
Explanation: Identical envelopes cannot nest.
