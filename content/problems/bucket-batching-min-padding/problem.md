A training job pads every batch of documents to the length of its longest
document, so a batch of $s$ documents whose longest has length $m$ costs
$s \cdot m$ token slots on the GPU, real and padding alike. Given the document
lengths and the number of GPUs `G`, split **all** the documents into exactly
`G` non-empty batches (one per GPU) so that the total number of token slots is
as small as possible, and return that minimum.

Documents can go into any batch in any combination; the order of `lengths`
means nothing.

## Constraints

- `1 <= G <= len(lengths) <= 200`
- `1 <= lengths[i] <= 10⁶`

## Examples

**Example 1**
```
Input:  lengths = [1, 3, 4, 7], G = 2
Output: 19
Explanation: [1, 3] [4, 7] costs 2·3 + 2·7 = 20, [1] [3, 4, 7] costs 1 + 21 = 22,
and [1, 3, 4] [7] costs 3·4 + 7 = 19, the best.
```

**Example 2**
```
Input:  lengths = [5, 1, 5, 1, 9], G = 3
Output: 21
Explanation: [1, 1] [5, 5] [9] costs 2 + 10 + 9 = 21, with no padding at all.
```

**Example 3**
```
Input:  lengths = [9, 1, 4, 7, 5, 10], G = 2
Output: 45
Explanation: [1, 4, 5] [7, 9, 10] costs 15 + 30 = 45. Cutting at the largest
jump between sorted lengths (from 1 to 4) gives [1] [4, 5, 7, 9, 10] = 1 + 50 = 51.
```
