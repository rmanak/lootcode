**AdaBoost** builds a strong classifier from many weak ones. Each round, it
fits a **decision stump** (a one-feature threshold rule) to weighted data. It
gives the stump a vote $\alpha$ based on how well it did, then raises the
weights of the examples the stump got wrong, so the next round focuses on them.
Implement one round.

`X` has $N$ rows (examples) $x_i$ of $d$ numeric features, `y` has the labels
$y_i$ (each $+1$ or $-1$), and `weights` has one positive weight $w_i$ per
example. The weights need not sum to 1.

**Stumps.** A stump is a feature $j$, a threshold $t$ and a polarity
$p \in \{+1, -1\}$:

$$
h(x) =
\begin{cases}
p & \text{if } x_j > t \\
-p & \text{if } x_j \le t
\end{cases}
$$

For each feature, the candidate thresholds are the **midpoints** between
consecutive distinct values the feature takes, as in a decision tree. Each
threshold is tried with both polarities.

**Error.** A stump's weighted error is the misclassified share of the total
weight:

$$
\varepsilon = \frac{\sum_{i \,:\, h(x_i) \ne y_i} w_i}{\sum_i w_i}
$$

Pick the stump with the **smallest error**. Break ties by the lowest feature,
then the lowest threshold, then polarity $+1$ before $-1$. Two errors that
differ by less than `1e-9` count as tied.

**Update.** With $\varepsilon$ the chosen stump's error and the $w_i$
normalized to sum to 1, the stump's vote and the reweighting are

$$
\begin{aligned}
\alpha &= \frac{1}{2} \ln \frac{1 - \varepsilon}{\varepsilon} \\
w_i &\leftarrow w_i\, e^{-\alpha\, y_i\, h(x_i)}
\end{aligned}
$$

and then the $w_i$ are normalized again to sum to 1.

**Return `[feature, threshold, polarity, alpha, newWeights]`**.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

The feature and polarity must match exactly. The other numbers are accepted
when within a relative `1e-6` (or an absolute `1e-9`) of the expected value.
In every test, any error not tied with the best exceeds it by more than `1e-6`.

## Constraints

- `2 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` numbers
- Every feature is a finite number with absolute value `<= 10⁴`
- `y` has `N` entries, each `1` or `-1`
- Every weight is a finite number with `1e-6 <= weights[i] <= 100`
- At least one feature takes two or more distinct values
- The best stump's error is at least `1e-3`, so `alpha` is finite

## Examples

**Example 1**
```
Input:  X = [[1.0], [2.0], [3.0], [4.0]], y = [-1, -1, 1, -1], weights = [1.0, 1.0, 1.0, 1.0]
Output: [0, 2.5, 1, 0.5493061443340549,
         [0.16666666666666666, 0.16666666666666666, 0.16666666666666666, 0.5000000000000001]]
Explanation: "+1 above 2.5" gets only the last example wrong, so ε = 1/4 and
alpha = ½ · ln 3. Each correct weight is multiplied by exp(−alpha) = 1/√3, and
the wrong one by √3. After normalizing, the misclassified example carries half
of the total weight.
```

**Example 2**
```
Input:  X = [[0.0, 5.0], [1.0, 3.0], [2.0, 4.0], [3.0, 1.0]], y = [1, -1, -1, 1],
        weights = [0.1, 0.4, 0.2, 0.3]
Output: [0, 2.5, 1, 1.0986122886681098,
         [0.5000000000000001, 0.22222222222222224, 0.11111111111111112, 0.16666666666666666]]
Explanation: the best stump misclassifies only example 0, so ε = 0.1 and
alpha = ½ · ln 9 = ln 3.
```

**Example 3**
```
Input:  X = [[1.0, 0.0], [2.0, 0.0], [3.0, 1.0], [4.0, 1.0]], y = [1, -1, 1, -1],
        weights = [1.0, 1.0, 1.0, 1.0]
Output: [0, 1.5, -1, 0.5493061443340549,
         [0.16666666666666666, 0.16666666666666666, 0.5, 0.16666666666666666]]
Explanation: two stumps on feature 0 tie at ε = 1/4: polarity −1 at 1.5 and
polarity −1 at 3.5. The lower threshold wins.
```
