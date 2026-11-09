An inference service stores very long integer vectors (quantized
activations, masks, sparse counts) that consist mostly of long stretches of
one repeated value. It keeps them **run-length encoded**: a list of
`[value, count]` pairs, meaning `count` copies of `value`, in order. For
example `[3, 3, 3, 0, 0, 0, 4, 4]` is stored as `[[3, 3], [0, 3], [4, 2]]`.

Given two encodings `a` and `b` of vectors with the **same total length**,
return their **dot product** $\sum_i a_i b_i$.

The decoded vectors can be far too long to build, so work with the runs
directly. The encodings are not necessarily minimal: two neighbouring runs
may hold the same value.

## Constraints

- `1 <= len(a), len(b) <= 10⁵`
- Every `count` is in `[1, 10⁹]`; every `value` is in `[-10⁴, 10⁴]`
- The counts of `a` and of `b` have the same sum

## Examples

**Example 1**
```
Input:  a = [[3, 3], [0, 3], [4, 2]], b = [[1, 4], [2, 4]]
Output: 25
Explanation: decoded, a = [3, 3, 3, 0, 0, 0, 4, 4] and b = [1, 1, 1, 1, 2, 2, 2, 2]:
3·1·3 + 0·1·1 + 0·2·2 + 4·2·2 = 9 + 16 = 25.
```

**Example 2**
```
Input:  a = [[5, 1000000000]], b = [[-2, 999999999], [7, 1]]
Output: -9999999955
Explanation: 5 · (−2) · 999999999 + 5 · 7 · 1.
```

**Example 3**
```
Input:  a = [[1, 2], [1, 2], [-1, 3]], b = [[2, 3], [3, 4]]
Output: 0
Explanation: the first two runs of a hold the same value; they still count
as separate runs. The products are 2 + 2 + 2 + 3 − 3 − 3 − 3 = 0.
```
