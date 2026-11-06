A colleague wrote a mini-batch SGD loop for L2-regularized logistic
regression. It runs without errors and the loss even goes down, but the
numbers are wrong. **The starter code is that loop. It has seven bugs.** Fix
them so the function does exactly what is specified below. (You may also
rewrite it from scratch.)

**The specification.** `X` has $N$ rows $x_i$ of $d$ features, and `y` holds
the labels $y_i$, each `0` or `1`. Write $\eta$ for `lr`, $\gamma$ for
`lrDecay` and $\lambda$ for `l2`. Start from $w = 0$ (length $d$) and $b = 0$,
with $\sigma(z) = 1 / (1 + e^{-z})$. Then, for each epoch
$e = 0, 1, \dots, \texttt{epochs} - 1$:

1. The step size is $\eta_e = \eta\, \gamma^{e}$, so the first epoch uses `lr`
   itself.
2. Visit the examples in the order `permutations[e]`, in consecutive batches of
   `batchSize`. The last batch is smaller when $N$ is not a multiple of
   `batchSize`. Each batch takes one step, below.
3. After the epoch, record the objective on the **whole** dataset, below.

**One step**, for a batch $\mathcal{B}$ of $m$ examples. The gradient of the
batch objective is computed fresh for each batch, and the bias is not
regularized:

$$
\begin{aligned}
\delta_i &= \sigma(x_i \cdot w + b) - y_i \\
g_w &= \frac{1}{m} \sum_{i \in \mathcal{B}} \delta_i\, x_i + \lambda\, w \\
g_b &= \frac{1}{m} \sum_{i \in \mathcal{B}} \delta_i \\
w &\leftarrow w - \eta_e\, g_w \\
b &\leftarrow b - \eta_e\, g_b
\end{aligned}
$$

**The recorded objective** is the mean log-loss plus the L2 penalty, with
$z_i = x_i \cdot w + b$:

$$
\begin{aligned}
\texttt{loss} &= \frac{1}{N} \sum_{i=1}^{N} \Big[ \log\left(1 + e^{z_i}\right) - y_i\, z_i \Big] \\
&\quad + \frac{\lambda}{2} \lVert w \rVert^2
\end{aligned}
$$

On separable data the margins grow large, and $\sigma(z)$ rounds to exactly
$0$ or $1$. The recorded loss must still be a finite number.

**Return `[w, b, lossHistory]`**, where `lossHistory` has one entry per epoch.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`. Every entry of `X` is finite with
  absolute value `<= 10`, and every label is `0` or `1`
- `1 <= epochs <= 20` and `1 <= batchSize <= 256` (it may exceed `N`)
- `0 < lr <= 5`, `0 < lrDecay <= 1` and `0 <= l2 <= 1`
- `permutations` has `epochs` rows, each a permutation of `0 … N − 1`

## Examples

**Example 1**
```
Input:  X = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, 0.0], [0.0, -1.0]], y = [1, 1, 1, 0, 0],
        epochs = 2, batchSize = 2, lr = 0.5, lrDecay = 0.5, l2 = 0.1,
        permutations = [[4, 0, 2, 1, 3], [1, 3, 0, 4, 2]]
Output: [[0.5947418080936571, 0.4744138941043659], 0.05025870075971862,
         [0.5040392812407499, 0.4549461700763581]]
Explanation: each epoch has batches of 2, 2 and 1. The first epoch steps with
0.5 and the second with 0.25. The starter gets this wrong in several ways.
```

**Example 2**
```
Input:  X = [[1.0], [2.0], [-1.0], [-2.0]], y = [1, 1, 0, 1], epochs = 3, batchSize = 4, lr = 1.0,
        lrDecay = 1.0, l2 = 0.0, permutations = [[0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]
Output: [[0.3969235370019731], 0.589213280958103, [0.5950086476834489, 0.5556515521134107, 0.5338491013733917]]
Explanation: one full batch per epoch, no decay, no regularization and the
identity order make this plain gradient descent. The starter happens to get
this one right.
```

**Example 3**
```
Input:  X = [[2.0, 1.0], [-1.0, 1.0], [0.5, -2.0]], y = [1, 0, 1], epochs = 1, batchSize = 1, lr = 0.1,
        lrDecay = 1.0, l2 = 0.0, permutations = [[2, 0, 1]]
Output: [[0.1731258784121465, -0.09812587841214648], 0.051874121587853525, [0.5611857931745907]]
Explanation: pure SGD, one example at a time, in the order 2, 0, 1. Each
example must be paired with its own label.
```
