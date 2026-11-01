# Dense Layer: Backward Pass

A dense (fully connected) layer computes, with $f$ the `activation` applied
element-wise and the bias $b$ added to every row,

$$
\begin{aligned}
Z &= X W + b \\
Y &= f(Z)
\end{aligned}
$$

for a batch `X` of $N$ rows with $D_\text{in}$ features, a weight matrix `W`
($D_\text{in} \times D_\text{out}$) and a bias `b` ($D_\text{out}$). During
backpropagation the layer receives `dY`, the gradient of the loss with respect
to its output ($N \times D_\text{out}$). It must return the gradients with
respect to its input and its parameters, where $\odot$ is the element-wise
product:

$$
\begin{aligned}
\texttt{dZ} &= \texttt{dY} \odot f'(Z) \\
\texttt{dX} &= \texttt{dZ}\; W^\top \\
\texttt{dW} &= X^\top\, \texttt{dZ} \\
\texttt{db} &= \sum_{n=1}^{N} \texttt{dZ}_n
\end{aligned}
$$

So `dX` is $N \times D_\text{in}$, `dW` is $D_\text{in} \times D_\text{out}$,
and `db` ($D_\text{out}$) is the rows of `dZ` **summed**, not averaged.

The activation is one of:

| `activation` | $f(z)$ | $f'(z)$ |
|---|---|---|
| `"linear"` | $z$ | $1$ |
| `"relu"` | $\max(z, 0)$ | $1$ if $z > 0$, else $0$ (so $f'(0) = 0$) |
| `"tanh"` | $\tanh z$ | $1 - \tanh^2 z$ |
| `"sigmoid"` | $\sigma(z) = 1 / (1 + e^{-z})$ | $\sigma(z)\,(1 - \sigma(z))$ |

The derivative is evaluated at the pre-activation $Z$, not at $Y$.

**Return `[dX, dW, db]`**.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. For `"relu"`, the tests never put a
pre-activation within `1e-9` of zero unless it is exactly zero, and then every
input is a multiple of $1/16$, so floating-point arithmetic computes it
exactly.

## Constraints

- `1 <= N <= 100` and `1 <= Din, Dout <= 32`
- `X` is `N × Din`, `W` is `Din × Dout`, `b` has `Dout` entries, and `dY` is
  `N × Dout`
- Every entry is a finite number with absolute value `<= 10`
- `activation` is `"linear"`, `"relu"`, `"tanh"` or `"sigmoid"`

## Examples

**Example 1**
```
Input:  X = [[1.0, 2.0], [-1.0, 1.0]], W = [[0.5, -1.0], [0.25, 0.5]], b = [0.0, 0.0],
        dY = [[1.0, 2.0], [3.0, -1.0]], activation = "relu"
Output: [[[0.5, 0.25], [1.0, -0.5]], [[1.0, 1.0], [2.0, -1.0]], [1.0, -1.0]]
Explanation: Z = [[1, 0], [−0.25, 1.5]]. The pre-activation of 0 has
relu' = 0, so dZ = [[1, 0], [0, −1]].
```

**Example 2**
```
Input:  X = [[1.0], [-2.0]], W = [[0.5, -0.5]], b = [0.0, 0.0], dY = [[1.0, 2.0], [1.0, -1.0]],
        activation = "tanh"
Output: [[[-0.3932238664829637], [0.41997434161402614]],
         [[-0.05350095026212487, 2.4128441491599073]],
         [1.2064220745799537, 1.1529211243178286]]
```

**Example 3**
```
Input:  X = [[1.0, 0.0], [0.0, 1.0]], W = [[2.0], [-1.0]], b = [1.0], dY = [[0.5], [-0.5]],
        activation = "linear"
Output: [[[1.0, -0.5], [-1.0, 0.5]], [[0.5], [-0.5]], [0.0]]
Explanation: with a linear activation dZ = dY. The bias gradient sums the two
rows, 0.5 + (−0.5) = 0.
```
