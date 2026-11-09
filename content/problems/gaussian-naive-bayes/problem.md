A **Gaussian naive Bayes** classifier models each feature, within each class,
as an independent normal distribution. Fit one on `X` (training rows) and `y`
(their integer labels), then predict a label for every row of `XTest`.

**Fit.** For every class $c$ that appears in `y`, with $n_c$ training rows out
of $n$:

$$
\begin{aligned}
\pi_c &= \frac{n_c}{n} \\[1ex]
\mu_{cj} &= \frac{1}{n_c} \sum_{i:\, y_i = c} X_{ij} \\[1ex]
\sigma^2_{cj} &= \frac{1}{n_c} \sum_{i:\, y_i = c} \left(X_{ij} - \mu_{cj}\right)^2 + 10^{-9}
\end{aligned}
$$

The variance is the **population** variance (divide by $n_c$, not $n_c - 1$),
plus $10^{-9}$ so that a feature that is constant within a class does not
divide by zero.

**Predict.** Score a test row $x$ against each class with the log of prior
times likelihood (natural log), and predict the class with the highest score:

$$
\operatorname{score}_c(x) = \log \pi_c + \sum_{j=1}^{d} \left[ -\tfrac{1}{2} \log\left(2\pi\, \sigma^2_{cj}\right) - \frac{(x_j - \mu_{cj})^2}{2\, \sigma^2_{cj}} \right]
$$

Work in log space: multiplying the raw densities underflows to $0$ once there
are a few dozen features. If two classes tie for the highest score, predict the
**smaller** label. (The tests never put two different scores within a relative
$10^{-9}$ of each other, so a tie only happens when the scores are equal.)

**Return** the list of predicted labels, one per row of `XTest`.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

## Constraints

- `1 <= n <= 1000` training rows and `1 <= m <= 1000` test rows
- `1 <= d <= 50` features, the same in `X` and `XTest`
- Every value is finite with absolute value `<= 10⁴`
- Labels are integers with absolute value `<= 10⁶`; at most `20` distinct labels

## Examples

**Example 1**
```
Input:  X = [[0.0], [2.0], [8.0], [10.0]], y = [0, 0, 1, 1], XTest = [[1.0], [9.0], [5.0]]
Output: [0, 1, 0]
Explanation: class 0 has mean 1 and class 1 has mean 9, both with variance 1
(plus 1e-9) and prior 1/2. The point 5 is exactly 4 from both means, so the
scores tie and the smaller label, 0, wins.
```

**Example 2**
```
Input:  X = [[1.0, 0.0], [1.0, 2.0], [3.0, 1.0], [5.0, 1.0], [5.0, 3.0]], y = [7, 7, 7, 2, 2],
        XTest = [[4.0, 1.0], [5.0, 1.5], [5.0, 9.0]]
Output: [7, 2, 2]
Explanation: class 7 (prior 3/5) has means [5/3, 1] and variances
[8/9, 2/3]. Class 2 (prior 2/5) has means [5, 2] and variances [0, 1], so its
feature-0 variance is just 1e-9. The first row's x₀ = 4 costs class 2 a
penalty of (4 − 5)² / (2·10⁻⁹) = 5·10⁸, and it goes to class 7. The other two
rows have x₀ = 5 exactly, which class 2 finds overwhelmingly likely, so they go
to class 2 even though 9 is far from its feature-1 mean.
```

**Example 3**
```
Input:  X = [[1.0], [1.0], [3.0], [3.0], [7.0], [9.0]], y = [1, 1, 1, 1, 0, 0],
        XTest = [[5.0], [2.0], [8.0]]
Output: [1, 1, 0]
Explanation: class 1 has mean 2 and class 0 has mean 8, and both have
population variance 1. The point 5 is 3 from each mean, so the likelihoods are
equal and the prior decides: class 1 has 4 of the 6 rows. (With the sample
variances 4/3 and 2 instead, class 0 would win.)
```
