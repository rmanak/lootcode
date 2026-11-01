# Two-Layer MLP: Backpropagation

Write the forward and backward pass of a small neural network classifier by
hand: one hidden layer with ReLU, then a softmax cross-entropy loss. This is
the classic "backprop from scratch" interview question.

`X` holds $N$ examples (rows) of $D$ features and `y` their class labels in
$0, \dots, C - 1$. Vectors are rows, and each bias is added to every row. With
$W_1, b_1, W_2, b_2$ = `W1`, `b1`, `W2`, `b2`:

$$
\begin{aligned}
A &= X W_1 + b_1 \\
R &= \operatorname{ReLU}(A) = \max(A, 0) \\
Z &= R\, W_2 + b_2 \\
L &= -\frac{1}{N} \sum_{i=1}^{N} \log \operatorname{softmax}(Z_i)_{y_i}
\end{aligned}
$$

The pre-activations $A$ and the hidden layer $R$ are $N \times H$, the logits
$Z$ are $N \times C$, and $L$ is the mean cross-entropy (natural log).

**Return `[L, dW1, db1, dW2, db2]`**: the loss and its gradients with respect to
each parameter, each with the same shape as that parameter ($D \times H$, $H$,
$H \times C$, $C$).

The ReLU has a kink at $0$. Use the convention **$\operatorname{ReLU}'(0) = 0$**:
a hidden unit whose pre-activation is exactly $0$ passes no gradient back, just
like one that is negative.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

**Numerical stability matters.** Some tests have logits in the hundreds or
thousands, past the point (about 709) where `exp` overflows a float.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 64`, `1 <= D <= 16`, `1 <= H <= 32`, `2 <= C <= 10`
- `X` is `N × D`, `W1` is `D × H`, `b1` has `H` entries, `W2` is `H × C`, and
  `b2` has `C` entries
- Every entry of `X`, `W1`, `b1`, `W2` and `b2` is a finite number with absolute
  value `<= 100`
- `y` has `N` entries, each an integer with `0 <= y[i] < C`

## Examples

**Example 1**
```
Input:  X = [[1.0, 2.0]], y = [1],
        W1 = [[1.0, -1.0], [0.5, 1.0]], b1 = [0.0, -1.0],
        W2 = [[1.0, -1.0], [2.0, 0.5]], b2 = [0.0, 0.0]
Output: [4.0181499279178094,
         [[1.964027580075817, 0.0], [3.928055160151634, 0.0]],
         [1.964027580075817, 0.0],
         [[1.964027580075817, -1.964027580075817], [0.0, 0.0]],
         [0.9820137900379085, -0.9820137900379085]]
Explanation: A = [2, 0], so Hd = [2, 0] and the logits are [2, −2]. The label
is 1, so L = log(1 + e⁴) ≈ 4.018. The second hidden unit sits exactly at the
kink, so with ReLU′(0) = 0 its column of dW1 and its entry of db1 are 0.
```

**Example 2**
```
Input:  X = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], y = [0, 1, 2],
        W1 = [[1.0, 2.0, -1.0], [-1.0, 1.0, 1.0]], b1 = [0.0, -1.0, 0.5],
        W2 = [[1.0, 0.0, -1.0], [0.0, 1.0, 1.0], [2.0, -1.0, 0.0]], b2 = [0.1, 0.0, -0.1]
Output: [2.0640036374423665,
         [[-0.227743159768412, 0.1115715406555978, 0.03590812773012472],
          [0.0, -0.07066090690250929, 1.0004816516938027]],
         [-0.227743159768412, 0.1115715406555978, 1.0004816516938027],
         [[-0.18223244755810708, 0.13672173534780216, 0.04551071221030493],
          [-0.04091063375308854, 0.3475491074975898, -0.30663847374450126],
          [0.5111520366229095, -0.44251027656476016, -0.06864176005814941]],
         [0.20564284812550543, -0.08800932497877537, -0.11763352314673009]]
Explanation: the pre-activations are [[1, 1, −0.5], [−1, 0, 1.5], [0, 2, 0.5]];
the 0s, like the negatives, block the gradient.
```

**Example 3**
```
Input:  X = [[2.0, -1.0], [-1.0, 3.0]], y = [0, 1],
        W1 = [[1.0, 1.0], [1.0, 2.0]], b1 = [-1.0, 0.0],
        W2 = [[3.0, -2.0], [-1.0, 1.0]], b2 = [0.5, -0.5]
Output: [0.16570580771801632,
         [[-0.04496552490522889, 0.017986209962091555], [0.13489657471568667, -0.053958629886274666]],
         [0.04496552490522889, -0.017986209962091555],
         [[0.008993104981045781, -0.008993104981045774], [0.044965524905228905, -0.04496552490522887]],
         [-0.12547760570395178, 0.12547760570395178]]
Explanation: the first example's pre-activations are both exactly 0, so it
reaches the output only through the biases: its hidden layer is all zeros.
```
