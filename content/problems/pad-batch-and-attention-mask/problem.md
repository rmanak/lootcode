A transformer processes a batch as one rectangular tensor, but the sequences
in a batch have different lengths. So each sequence is **padded** to a common
length, and the model is told which positions are real. Build everything a
decoder-only model needs for one batch.

`sequences` is a list of $B$ token-id lists. With $\ell$ the length of the
longest one and $m$ = `padToMultipleOf`, every row is padded to $\ell$ rounded
up to a multiple of $m$:

$$
L = m \left\lceil \frac{\ell}{m} \right\rceil
$$

(GPU kernels run faster on multiples of 8). Padding uses the token `padId`.
With `side = "right"` the pad tokens go after the sequence; with
`side = "left"` they go before it, which is what batched generation uses.

Return four things, each with one entry per sequence, in order:

1. **`inputIds`** ($B \times L$): the padded rows.
2. **`attentionMask`** ($B \times L$): `1` at a real token, `0` at padding.
   Work it out from the lengths. **`padId` can also appear as a real token
   inside a sequence**, so comparing ids with `padId` is wrong.
3. **`positionIds`** ($B \times L$): each real token's position among the real
   tokens of its row, counting from `0`. That is the same position it would
   have without any padding. Padding positions get `0`.
4. **`causalMask`** ($B \times L \times L$): for each row, `causalMask[i][j]`
   is `1` when query position $i$ may attend to key position $j$. That
   requires $j \le i$ (no looking ahead), with **both** $i$ and $j$ real
   tokens. A padding query attends to nothing, so its whole row is `0`.

**Return `[inputIds, attentionMask, positionIds, causalMask]`**.

Answers must match exactly.

## Constraints

- `1 <= len(sequences) <= 16`
- Every sequence has `1` to `32` tokens, and every token is an integer in
  `[0, 50000]`
- `padId` is an integer in `[0, 50000]`
- `side` is `"left"` or `"right"`
- `1 <= padToMultipleOf <= 8`

## Examples

**Example 1**
```
Input:  sequences = [[5, 6, 7], [8]], padId = 0, side = "right", padToMultipleOf = 1
Output: [[[5, 6, 7], [8, 0, 0]],
         [[1, 1, 1], [1, 0, 0]],
         [[0, 1, 2], [0, 0, 0]],
         [[[1, 0, 0], [1, 1, 0], [1, 1, 1]], [[1, 0, 0], [0, 0, 0], [0, 0, 0]]]]
Explanation: the second row's last two positions are padding. Their query rows
in the causal mask are all 0, and no query attends to them.
```

**Example 2**
```
Input:  sequences = [[11, 12], [13, 14, 15]], padId = 0, side = "left", padToMultipleOf = 1
Output: [[[0, 11, 12], [13, 14, 15]],
         [[0, 1, 1], [1, 1, 1]],
         [[0, 0, 1], [0, 1, 2]],
         [[[0, 0, 0], [0, 1, 0], [0, 1, 1]], [[1, 0, 0], [1, 1, 0], [1, 1, 1]]]]
Explanation: with left padding, token 11 sits in column 1 but its position id
is 0, because it is the first real token.
```

**Example 3**
```
Input:  sequences = [[2, 0, 9], [4, 4]], padId = 0, side = "right", padToMultipleOf = 4
Output: [[[2, 0, 9, 0], [4, 4, 0, 0]],
         [[1, 1, 1, 0], [1, 1, 0, 0]],
         [[0, 1, 2, 0], [0, 1, 0, 0]],
         [[[1, 0, 0, 0], [1, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]],
          [[1, 0, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]]]
Explanation: the longest sequence has 3 tokens, rounded up to L = 4. The 0 in
[2, 0, 9] is a real token, so its mask is 1, even though 0 is also the padId.
```
