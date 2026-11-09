A stack of $N$ square matrices $W_0, \dots, W_{N-1}$ (each $D \times D$) is
multiplied into **all** of its prefix products, the matrix analogue of a
cumulative sum:

$$
P_i = W_0 W_1 \cdots W_i \qquad (i = 0, \dots, N - 1)
$$

The order matters: matrix multiplication is associative but not commutative.
This is the forward pass of a custom autograd operator (it shows up in linear
recurrences and state-space models). Write its forward **and** its
hand-written backward pass.

**Backward.** Some loss $L$ depends on every output, and `dP[i]` is the
upstream gradient $\partial L / \partial P_i$. Compute
$\texttt{dW}[j] = \partial L / \partial W_j$ for every $j$. Each $W_j$ feeds
every later product $P_i$ with $i \ge j$, so its gradient sums a contribution
from each of them. The total is the same as differentiating

$$
L = \sum_{i=0}^{N-1} \sum_{r, c} \texttt{dP}[i]_{rc}\, (P_i)_{rc}
$$

Recomputing each contribution from scratch costs $O(N^2 D^3)$. Find the
$O(N D^3)$ way: one forward sweep and one reverse sweep, the way backprop
through a cumulative sum accumulates a running suffix sum.

**Return `[P, dW]`**, both $N \times D \times D$, in the order of `W`.

You may use **numpy** and the Python standard library. Numpy arrays are fine as
return values.

## Constraints

- `1 <= N <= 60` and `1 <= D <= 6`
- `W` and `dP` are `N × D × D`; every entry is finite with absolute value `<= 2`
- The tests keep every prefix product and gradient entry below `10⁶` in
  absolute value

## Examples

**Example 1**
```
Input:  W = [[[2.0]], [[1.5]], [[-1.0]]], dP = [[[1.0]], [[1.0]], [[1.0]]]
Output: [[[[2.0]], [[3.0]], [[-3.0]]], [[[1.0]], [[0.0]], [[3.0]]]]
Explanation: with 1 × 1 matrices, L = w₀ + w₀w₁ + w₀w₁w₂. Its partial
derivatives are 1 + w₁ + w₁w₂ = 1, w₀ + w₀w₂ = 0 and w₀w₁ = 3.
```

**Example 2**
```
Input:  W = [[[1.0, 1.0], [0.0, 1.0]], [[0.0, 1.0], [1.0, 0.0]]],
        dP = [[[0.0, 0.0], [0.0, 0.0]], [[1.0, 0.0], [0.0, 0.0]]]
Output: [[[[1.0, 1.0], [0.0, 1.0]], [[1.0, 1.0], [1.0, 0.0]]],
         [[[0.0, 1.0], [0.0, 0.0]], [[1.0, 0.0], [1.0, 0.0]]]]
Explanation: only the top-left entry of P₁ = W₀W₁ matters. Its gradient
reaches W₁ as P₀ᵀ·dP₁ and W₀ as dP₁·W₁ᵀ.
```

**Example 3**
```
Input:  W = [[[1.0, 2.0], [0.0, 1.0]], [[0.5, 0.0], [1.0, -1.0]], [[0.0, 1.0], [-1.0, 0.0]]],
        dP = [[[1.0, 0.0], [0.0, 1.0]], [[0.0, 1.0], [0.0, 0.0]], [[1.0, -1.0], [2.0, 0.0]]]
Output: [[[[1.0, 2.0], [0.0, 1.0]], [[2.5, -2.0], [1.0, -1.0]], [[2.0, 2.5], [1.0, 1.0]]],
         [[[0.5, -1.0], [0.0, 3.0]], [[-1.0, 0.0], [-2.0, -2.0]], [[4.5, -2.5], [-4.0, 2.0]]]]
Explanation: every output now has an upstream gradient, so dW₀ collects
contributions from P₀, P₁ and P₂, and dW₁ from P₁ and P₂.
```
