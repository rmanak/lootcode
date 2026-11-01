# Logistic Regression by Gradient Descent

**Logistic regression** predicts the probability that an example is positive as
$\sigma(w \cdot x + b)$, where $\sigma(z) = 1 / (1 + e^{-z})$. It is trained by
minimizing the mean **binary cross-entropy** (log loss) over the training set.

Train it with plain full-batch gradient descent, exactly as follows. `X` has
$N$ rows (examples) $x_i$ of $d$ features, $y_i$ = `y[i]` is `0` or `1`, and
$\eta$ = `lr`. Start from $w = 0$ ($d$ zeros) and $b = 0$, then repeat `steps`
times. First compute, for every example $i$, the prediction and the loss
(natural log):

$$
\begin{aligned}
z_i &= w \cdot x_i + b \\
p_i &= \sigma(z_i) \\
L &= -\frac{1}{N} \sum_{i=1}^{N} \Big[ y_i \log p_i + (1 - y_i) \log (1 - p_i) \Big]
\end{aligned}
$$

Record $L$ (the loss **before** this step's update). Then take the gradients
of $L$ with respect to $w$ and $b$, and update both using the old $w$ and $b$:

$$
\begin{aligned}
g_w &= \frac{1}{N} \sum_{i=1}^{N} (p_i - y_i)\, x_i \\
g_b &= \frac{1}{N} \sum_{i=1}^{N} (p_i - y_i) \\
w &\leftarrow w - \eta\, g_w \\
b &\leftarrow b - \eta\, g_b
\end{aligned}
$$

**Return `[w, b, lossHistory]`**: the final weights (a list of $d$ numbers),
the final bias, and the `steps` recorded losses in order. The first recorded
loss is always $\log 2$, because every prediction starts at
$\sigma(0) = \tfrac{1}{2}$.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

**Numerical stability matters.** Features in the tests reach $\pm 100$, so
$z_i$ can grow into the thousands. Then $p_i$ rounds to exactly $0$ or $1$ and
the formula for $L$ as written takes $\log 0$. Compute the loss in a form that
stays exact: no epsilon clipping, because a confidently wrong example has to
cost its full amount.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every feature is a finite number with absolute value `<= 100`
- `y` has `N` entries, each `0` or `1`
- `0 < lr <= 10`
- `1 <= steps <= 1000`

## Examples

**Example 1**
```
Input:  X = [[1.0], [2.0], [-1.0], [-2.0]], y = [1, 1, 0, 1], lr = 0.5, steps = 3
Output: [[0.2719175565490306], 0.3311447732469863,
         [0.6931471805599453, 0.6374522249739495, 0.6022311297859285]]
Explanation: at the start every pᵢ is 0.5, so L = log 2 and pᵢ − yᵢ is
[−0.5, −0.5, 0.5, −0.5]. That gives gw = [−0.25] and gb = −0.25, so the first
step moves w to [0.125] and b to 0.125. Two more steps give the final values.
```

**Example 2**
```
Input:  X = [[0.0, 1.0], [1.0, 1.0], [2.0, -1.0]], y = [0, 1, 1], lr = 1.0, steps = 2
Output: [[0.7649192411500784, -0.2770226195092998], 0.19538306537473007,
         [0.6931471805599453, 0.4670622299392]]
```

**Example 3**
```
Input:  X = [[3.0, -1.0], [-2.0, 4.0]], y = [1, 0], lr = 0.1, steps = 1
Output: [[0.125, -0.125], 0.0, [0.6931471805599453]]
Explanation: pᵢ − yᵢ is [−0.5, 0.5], so gw = [−1.25, 1.25] and gb = 0.
One step of size 0.1 moves w to [0.125, −0.125] and leaves b at 0. The single
recorded loss is the one before that step, log 2.
```
