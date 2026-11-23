A **max-pooling** layer slides a $k_H \times k_W$ window over each channel of
its input and keeps the largest value in each window. There is no padding.
Implement its forward pass and its backward pass.

`x` is $C \times H \times W$. With `kernel` = $[k_H, k_W]$ and step $s$ =
`stride` in both directions, the output is $C \times H_\text{out} \times
W_\text{out}$:

$$
\begin{aligned}
H_\text{out} &= \left\lfloor \frac{H - k_H}{s} \right\rfloor + 1 \\[1ex]
W_\text{out} &= \left\lfloor \frac{W - k_W}{s} \right\rfloor + 1 \\[1ex]
\texttt{out}_{q,r,c} &= \max_{\substack{0 \le i < k_H \\ 0 \le j < k_W}} x_{q,\; rs + i,\; cs + j}
\end{aligned}
$$

**Backward.** `dout` ($C \times H_\text{out} \times W_\text{out}$) is the
gradient of the loss with respect to `out`. Each window passes all of its
gradient to the one input position that produced its maximum. Every other
position in the window gets nothing from it. When $s < k_H$ or $s < k_W$,
windows overlap and one input position can win several of them; its gradient
is the **sum** of what it receives.

**Ties.** When a window's maximum appears more than once, the winner is the
**first** occurrence in row-major order: the smallest $i$, and among those the
smallest $j$. That is what `torch.argmax` returns for a flattened window.

**Return `[out, dx]`**, where `dx` has the shape of `x`.

Write it in **PyTorch** (`torch` is already imported). `x` and `dout` arrive as
float32 tensors and `kernel` and `stride` as plain Python values. Return the
structure described above with a tensor in place of each list of numbers and a
0-dim tensor in place of each single number (float32; int64 for integers). The
examples print tensors as nested lists. **Autograd is off-limits**: derive the
gradients by hand (`.backward()`, `torch.autograd` and `torch.func` raise).
These built-ins would do the exercise for you and raise if called:
`torch.nn.functional.max_pool2d`, `torch.nn.functional.max_pool2d_with_indices`,
`torch.max_pool2d`, `torch.nn.functional.max_pool1d`, `torch.max_pool1d`,
`torch.nn.functional.max_pool3d`, `torch.max_pool3d`,
`torch.nn.functional.adaptive_max_pool2d`, `torch.nn.functional.max_unpool2d`
(and their `torch.ops.aten` kernels).

Your answer is checked against the reference implementation with
`torch.allclose` semantics (`rtol=1e-5`, `atol=1e-6`), and every tensor's shape
and dtype must match exactly. Besides the stored tests, every run adds 5 hidden
tests drawn at random within the constraints.

## Constraints

- `1 <= C <= 8` and `1 <= H, W <= 32`
- `kernel = [kH, kW]` with `1 <= kH <= H` and `1 <= kW <= W`
- `1 <= stride <= 4`
- Every value in `x` is finite with absolute value `<= 100`
- `dout` is `C × Hout × Wout`, and every value is finite with absolute value
  `<= 10`

## Examples

**Example 1**
```
Input:  x = [[[1.0, 3.0, 2.0, 0.0], [4.0, 2.0, 1.0, 5.0], [0.0, 1.0, 6.0, 2.0], [3.0, 2.0, 1.0, 1.0]]],
        dout = [[[1.0, 2.0], [3.0, 4.0]]], kernel = [2, 2], stride = 2
Output: [[[[4.0, 5.0], [3.0, 6.0]]],
         [[[0.0, 0.0, 0.0, 0.0], [1.0, 0.0, 0.0, 2.0], [0.0, 0.0, 4.0, 0.0], [3.0, 0.0, 0.0, 0.0]]]]
Explanation: four separate 2 × 2 windows. Each gradient goes to its window's
maximum: 4 at (1, 0), 5 at (1, 3), 3 at (3, 0) and 6 at (2, 2).
```

**Example 2**
```
Input:  x = [[[2.0, 7.0, 7.0], [7.0, 1.0, 0.0]]], dout = [[[1.0, 10.0]]], kernel = [2, 2], stride = 1
Output: [[[[7.0, 7.0]]], [[[0.0, 11.0, 0.0], [0.0, 0.0, 0.0]]]]
Explanation: the first window [[2, 7], [7, 1]] has its maximum at (0, 1) and
at (1, 0). Row-major order picks (0, 1). The second window [[7, 7], [1, 0]]
picks its first 7, which is also (0, 1). So that position receives 1 + 10.
```

**Example 3**
```
Input:  x = [[[1.0, 5.0, 2.0], [0.0, 3.0, 4.0], [2.0, 1.0, 0.0]]], dout = [[[1.0, 2.0], [3.0, 4.0]]],
        kernel = [2, 2], stride = 1
Output: [[[[5.0, 5.0], [3.0, 4.0]]], [[[0.0, 3.0, 0.0], [0.0, 3.0, 4.0], [0.0, 0.0, 0.0]]]]
Explanation: the top two windows overlap, and both pick the 5 at (0, 1), so
it accumulates 1 + 2 = 3.
```
