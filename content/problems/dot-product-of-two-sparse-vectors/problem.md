Feature vectors in recommendation and search models are huge and almost
entirely zero: a user's vector over a billion items has a few hundred
non-zero entries. Such a vector is stored as a list of its non-zero entries.

`a` and `b` are two vectors of the same (huge) dimension in this form: each
is a list of `[index, value]` pairs with **strictly increasing** indices and
non-zero values. Every index not listed holds $0$. Return their **dot
product** $\sum_i a_i b_i$.

The two lists can differ wildly in length. Aim for time close to
$O(\min(|a|, |b|) \cdot \log \max(|a|, |b|))$ when one is much shorter, and
$O(|a| + |b|)$ otherwise.

## Constraints

- `0 <= len(a), len(b) <= 10⁵`
- `0 <= index < 10⁹`, strictly increasing within each list
- Every value is a non-zero integer in `[-10⁴, 10⁴]`

## Examples

**Example 1**
```
Input:  a = [[0, 1], [3, 2], [4, 3]], b = [[1, 5], [3, 4], [4, -1]]
Output: 5
Explanation: only indices 3 and 4 are non-zero in both: 2 · 4 + 3 · (−1) = 5.
```

**Example 2**
```
Input:  a = [[1, 2]], b = [[0, 3], [2, 1]]
Output: 0
```

**Example 3**
```
Input:  a = [[2, 4], [7, 1], [999999999, -2]], b = [[2, 4], [999999999, 5]]
Output: 6
Explanation: 4 · 4 + (−2) · 5 = 6. Pairing entries by position in the lists
instead of by index would give 4 · 4 + 1 · 5 = 21.
```
