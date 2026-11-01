# Softmax Regression by Gradient Descent

**Softmax regression** (multinomial logistic regression) is the multi-class
version of logistic regression. A linear map gives each class a score (a
**logit**), and the softmax turns the scores into probabilities. Train it with
plain full-batch gradient descent on the mean cross-entropy loss, exactly as
follows.

`X` has $N$ rows (examples) $x_i$ of $d$ features. $y_i$ = `y[i]` is the class
of example $i$, an integer in $[0, C)$ where $C$ = `numClasses`. Some classes
may not appear in `y`, but they still get a column of weights. $\eta$ is `lr`.

Start from $W = 0$ ($d \times C$ zeros) and $b = 0$ ($C$ zeros), then repeat
`steps` times. First compute every example's logits $z_i$ (one per class), its
softmax probabilities $p_i$, and the mean cross-entropy $L$:

$$
\begin{aligned}
z_i &= x_i W + b \\
p_{ic} &= \frac{e^{z_{ic}}}{\sum_k e^{z_{ik}}} \\
L &= -\frac{1}{N} \sum_{i=1}^{N} \log p_{i y_i}
\end{aligned}
$$

Record $L$ (the loss **before** this step's update). Then, with $G_i$ the
gradient of $L$ with respect to $z_i$, update both parameters ($W$ gets a
$d \times C$ update):

$$
\begin{aligned}
G_i &= \frac{1}{N} \left(p_i - \operatorname{onehot}(y_i)\right) \\
W &\leftarrow W - \eta \sum_{i=1}^{N} x_i^\top G_i \\
b &\leftarrow b - \eta \sum_{i=1}^{N} G_i
\end{aligned}
$$

**Return `[W, b, lossHistory]`**:
- `W`: $d$ rows of $C$ numbers
- `b`: $C$ numbers
- `lossHistory`: the `steps` recorded losses, in order

**Numerical stability matters.** Some tests use large learning rates, and the
logits reach the thousands. $e^{1000}$ overflows a float. In a badly
misclassified example the true class's probability also underflows to $0$, so
$\log p$ is $-\infty$ even when the softmax itself was computed stably. Compute
the loss in log space, with log-sum-exp.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every feature is a finite number with absolute value `<= 100`
- `2 <= numClasses <= 10`, and `y` has `N` integers in `[0, numClasses)`
- `0 < lr <= 10`
- `1 <= steps <= 500`

## Examples

**Example 1**
```
Input:  X = [[1.0], [-1.0]], y = [0, 1], numClasses = 2, lr = 0.5, steps = 2
Output: [[[0.4387703343990727, -0.4387703343990727]], [0.0, 0.0],
         [0.6931471805599453, 0.4740769841801067]]
Explanation: all the logits start at 0, so every probability is 1/2 and the
first loss is log 2. Then G = [[−¼, ¼], [¼, −¼]], so the first step moves W to
[[0.25, −0.25]]. The bias gradient sums to zero because the classes are
balanced.
```

**Example 2**
```
Input:  X = [[1.0, 0.0], [0.0, 1.0], [-1.0, -1.0]], y = [0, 1, 2], numClasses = 3,
        lr = 1.0, steps = 3
Output: [[[0.7877045555517711, -0.08624984133296443, -0.7014547142188067],
          [-0.08624984133296443, 0.7877045555517711, -0.7014547142188067]],
         [0.015999913752416467, 0.015999913752416467, -0.03199982750483288],
         [1.0986122886681098, 0.7184672109557333, 0.5197591851324426]]
Explanation: the first loss is log 3.
```

**Example 3**
```
Input:  X = [[2.0], [0.0], [1.0]], y = [1, 0, 0], numClasses = 3, lr = 0.3, steps = 2
Output: [[[-0.008544778101426792, 0.18387667673769403, -0.17533189863626716]],
         [0.19076834331153464, -0.009526888511147101, -0.18124145480038753],
         [1.0986122886681098, 0.9770090000969859]]
Explanation: class 2 never appears in y, so its weights and its bias go down.
numClasses, not the labels, decides how many columns W has.
```
