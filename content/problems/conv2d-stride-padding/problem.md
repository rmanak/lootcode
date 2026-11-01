# 2-D Convolution with Stride and Padding

Implement the forward pass of a 2-D convolution layer, as in
`torch.nn.Conv2d`, for a single image.

- `x` is the input: $C_\text{in} \times H \times W$ (channels, rows, columns).
- `weight` holds $C_\text{out}$ filters, each $C_\text{in} \times k_H \times k_W$,
  so it is $C_\text{out} \times C_\text{in} \times k_H \times k_W$.
- `bias` has $C_\text{out}$ entries, one per filter.
- `padding` adds that many rows or columns of **zeros on every side** (top,
  bottom, left and right) of each input channel.
- `stride` is the step between neighbouring filter positions, in both
  directions.

With $p$ = `padding` and $s$ = `stride`, the output has $C_\text{out}$ channels
of size $H_\text{out} \times W_\text{out}$:

$$
\begin{aligned}
H_\text{out} &= \left\lfloor \frac{H + 2p - k_H}{s} \right\rfloor + 1 \\[1ex]
W_\text{out} &= \left\lfloor \frac{W + 2p - k_W}{s} \right\rfloor + 1
\end{aligned}
$$

Output channel $o$ at row $r$ and column $c$ is, with $y$ = the output,
$w$ = `weight`, $b$ = `bias` and $\tilde x$ the zero-padded input,

$$
y_{o,r,c} = b_o + \sum_{q,\, i,\, j} w_{o,q,i,j}\; \tilde x_{q,\; rs + i,\; cs + j}
$$

where the sum runs over every input channel $q$, filter row
$0 \le i < k_H$ and filter column $0 \le j < k_W$. Deep-learning "convolution"
is really **cross-correlation**: the filter is **not** flipped.

**Return the $C_\text{out} \times H_\text{out} \times W_\text{out}$ output**.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= Cin, Cout <= 8` and `1 <= H, W <= 32`
- `1 <= kH, kW <= 7`, with `kH <= H + 2·padding` and `kW <= W + 2·padding`
  (so the output is at least `1 × 1`)
- `1 <= stride <= 4` and `0 <= padding <= 3`
- Every number in `x`, `weight` and `bias` is finite, with absolute value
  `<= 10`

## Examples

**Example 1**
```
Input:  x = [[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]],
        weight = [[[[1.0, 0.0], [0.0, -1.0]]]], bias = [0.0], stride = 1, padding = 0
Output: [[[-4.0, -4.0], [-4.0, -4.0]]]
Explanation: each output is the top-left value of a 2 × 2 window minus its
bottom-right value, for example 1 − 5 = −4. Flipping the filter would give +4.
```

**Example 2**
```
Input:  x = [[[1.0, 2.0, 0.0, 1.0], [0.0, 1.0, 3.0, 2.0], [2.0, 0.0, 1.0, 1.0], [1.0, 1.0, 0.0, 2.0]]],
        weight = [[[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]]], bias = [0.5],
        stride = 2, padding = 1
Output: [[[4.5, 9.5], [5.5, 11.5]]]
Explanation: the padded input is 6 × 6, so Hout = Wout = floor((6 − 3) / 2) + 1
= 2. The top-left window covers one row and one column of padding, so it sums
1 + 2 + 0 + 1 = 4, plus the bias of 0.5.
```

**Example 3**
```
Input:  x = [[[1.0, 0.0, 2.0, 1.0, 0.0], [0.0, 1.0, 1.0, 0.0, 2.0]],
             [[2.0, 1.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 1.0, 1.0]]],
        weight = [[[[1.0, 2.0]], [[0.0, -1.0]]], [[[0.5, 0.5]], [[1.0, 0.0]]]],
        bias = [1.0, -1.0], stride = 2, padding = 0
Output: [[[1.0, 5.0]], [[1.5, 0.5]]]
Explanation: two input channels, two filters of size 1 × 2. Hout =
floor((2 − 1) / 2) + 1 = 1 and Wout = floor((5 − 2) / 2) + 1 = 2. Rounding up
would give a third column. Each output sums over both input channels.
```
