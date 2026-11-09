A language model's training loss is a cross-entropy over every token position,
with two refinements that every real training loop has. **Masking**: padding
and prompt tokens must not contribute to the loss. **Label smoothing**: instead
of a one-hot target, train toward a target that keeps a little probability on
every class, which stops the model from becoming overconfident. Implement the
loss and its gradient.

`logits` has $N$ rows (positions) of $C$ class scores, `targets[i]` is the
correct class $y_i$ of position $i$, and `mask[i]` is $1$ if position $i$
counts and $0$ if it is ignored. With $\varepsilon$ = `smoothing`, each
position's softmax $p_i$ and smoothed target $q_i$ are

$$
\begin{aligned}
p_{ij} &= \frac{e^{z_{ij}}}{\sum_{k=1}^{C} e^{z_{ik}}} \\[1ex]
q_{ij} &= (1 - \varepsilon)\,[\,j = y_i\,] + \frac{\varepsilon}{C}
\end{aligned}
$$

so the target class gets $1 - \varepsilon + \varepsilon / C$ and every other
class $\varepsilon / C$ (the convention of PyTorch's `label_smoothing`). The
loss is the mean, over the $M = \sum_i \texttt{mask}_i$ counted positions, of
each position's cross-entropy against its smoothed target (natural log):

$$
L = \frac{1}{M} \sum_{i:\, \texttt{mask}_i = 1} \; \sum_{j=1}^{C} -q_{ij} \log p_{ij}
$$

If no position counts ($M = 0$), the loss is $0$ and so is every gradient.

**Return `[L, grad]`**, where `grad[i][j]` $= \partial L / \partial z_{ij}$ has
the shape of `logits`. Ignored positions get a row of zeros.

**Numerical stability matters.** Logits in the tests reach $\pm 1000$. With
label smoothing, every class's $\log p_{ij}$ enters the loss, including classes
whose probability underflows to $0$; compute the log-softmax directly as
$z_{ij} - \max_k z_{ik} - \log \sum_k e^{z_{ik} - \max_k z_{ik}}$.

You may use **numpy** and the Python standard library. Numpy arrays and
scalars are fine as return values.

## Constraints

- `1 <= N <= 500` and `2 <= C <= 100`
- Every logit is finite with absolute value `<= 1000`
- `0 <= targets[i] < C` for every position (masked ones included)
- Every `mask[i]` is `0` or `1`
- `0 <= smoothing < 1`

## Examples

**Example 1**
```
Input:  logits = [[2.0, 0.0, 0.0], [0.0, 0.0, 0.0]], targets = [0, 2], mask = [1, 1], smoothing = 0.0
Output: [0.6690785274449972, [[-0.1065069789192008, 0.05325348945960037, 0.05325348945960037],
                              [0.16666666666666666, 0.16666666666666666, -0.33333333333333337]]]
Explanation: no smoothing, so this is plain cross-entropy. Row 0 gives its
target probability e²/(e² + 2) ≈ 0.787 and costs ≈ 0.2395; row 1 is uniform
and costs log 3 ≈ 1.0986. The mean is ≈ 0.669, and each gradient row is
(p − onehot) / 2.
```

**Example 2**
```
Input:  logits = [[1.0, 2.0], [3.0, -1.0], [0.5, 0.5]], targets = [1, 0, 1], mask = [1, 0, 1], smoothing = 0.2
Output: [0.5532044340390843, [[0.08447071068499752, -0.08447071068499762], [0.0, 0.0],
                              [0.19999999999999996, -0.20000000000000004]]]
Explanation: with C = 2 and ε = 0.2 the target class gets 0.9 and the other
0.1. Row 0 costs −0.1·log 0.2689 − 0.9·log 0.7311 ≈ 0.4133 and row 2 costs
log 2 ≈ 0.6931. Row 1 is masked, so M = 2, the loss is their mean, and row 1's
gradient is zero.
```

**Example 3**
```
Input:  logits = [[1000.0, -1000.0, 0.0]], targets = [0], mask = [1], smoothing = 0.3
Output: [299.99999999999994, [[0.20000000000000007, -0.09999999999999999, -0.09999999999999999]]]
Explanation: q = [0.8, 0.1, 0.1] and the log-probabilities are about
[0, −2000, −1000], so the loss is 0.1·2000 + 0.1·1000 = 300. The softmax
itself is [1, 0, 0] to double precision; taking log of it would give −∞.
```
