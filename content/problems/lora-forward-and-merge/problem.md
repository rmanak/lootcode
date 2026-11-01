# LoRA: Forward Pass and Weight Merge

**LoRA** (low-rank adaptation) fine-tunes a big model without touching its
weights. A frozen weight matrix $W$ gets a trainable low-rank update $AB$,
where $A$ is $d_\text{in} \times r$ and $B$ is $r \times d_\text{out}$ with a
small rank $r$. That trains $r\,(d_\text{in} + d_\text{out})$ numbers instead
of $d_\text{in}\, d_\text{out}$. Implement the adapted layer's forward pass,
and the **merge** that folds the adapter back into $W$ for deployment.

Vectors are rows, so a batch $X$ is $N \times d_\text{in}$. With $s$ the
scaling, the output $Y$ ($N \times d_\text{out}$) and the merged weight
($d_\text{in} \times d_\text{out}$) are

$$
\begin{aligned}
Y &= X W + s\, (X A)\, B \\
\texttt{mergedW} &= W + s\, A B
\end{aligned}
$$

After merging, $X \cdot \texttt{mergedW}$ equals $Y$, so inference costs no
more than the original layer.

The **scaling** keeps the update's size stable as the rank changes. With
$\alpha$ = `alpha`:

- standard LoRA: $s = \alpha / r$
- **rsLoRA** (rank-stabilized, when `useRsLora` is true):
  $s = \alpha / \sqrt{r}$

**Return `[Y, mergedW]`**.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `X` is `N × din`, `W` is `din × dout`, `A` is `din × r` and `B` is
  `r × dout`
- `1 <= N, din, dout <= 64` and `1 <= r <= min(16, din, dout)`
- Every entry is finite with absolute value `<= 10`
- `0 < alpha <= 128`, and `useRsLora` is a boolean

## Examples

**Example 1**
```
Input:  X = [[1.0, 2.0]], W = [[1.0, 0.0], [0.0, 1.0]], A = [[1.0], [0.0]], B = [[0.0, 1.0]],
        alpha = 2.0, useRsLora = false
Output: [[[1.0, 4.0]], [[1.0, 2.0], [0.0, 1.0]]]
Explanation: r = 1, so scaling = 2. A · B adds 1 at row 0, column 1, scaled
to 2. Then X · mergedW = [1, 1·2 + 2·1] = [1, 4].
```

**Example 2**
```
Input:  X = [[1.0, 0.0, 1.0], [0.0, 2.0, -1.0]], W = [[1.0, 2.0], [0.0, 1.0], [-1.0, 0.0]],
        A = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], B = [[0.5, 0.0], [0.0, -0.5]],
        alpha = 8.0, useRsLora = false
Output: [[[4.0, 0.0], [-1.0, 0.0]], [[3.0, 2.0], [0.0, -1.0], [1.0, -2.0]]]
Explanation: r = 2, so scaling = 8 / 2 = 4.
```

**Example 3**
```
Input:  the same X, W, A, B and alpha as Example 2, with useRsLora = true
Output: [[[5.65685424949238, -0.8284271247461898], [-1.8284271247461898, -0.8284271247461898]],
         [[3.82842712474619, 2.0], [0.0, -1.8284271247461898], [1.8284271247461898, -2.82842712474619]]]
Explanation: rsLoRA uses scaling = 8 / √2 ≈ 5.657 instead of 4.
```
