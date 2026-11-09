**Bernoulli naive Bayes** classifies rows of **binary** features: each feature
says whether something is present (a word occurs in a message, a user clicked
a category). It models feature $j$ in class $c$ as a coin that comes up $1$
with probability $\theta_{cj}$, independently of the other features. Fit it on
`X` and their labels `y`, then predict a label for every row of `XTest`.

**Fit.** For every class $c$ that appears in `y`, with $n_c$ of the $n$
training rows, and with $\alpha$ = `alpha` (Laplace smoothing):

$$
\begin{aligned}
\pi_c &= \frac{n_c}{n} \\[1ex]
\theta_{cj} &= \frac{N_{cj} + \alpha}{n_c + 2\alpha}
\end{aligned}
$$

where $N_{cj}$ counts the class-$c$ rows with $X_{ij} = 1$. The smoothing keeps
every $\theta_{cj}$ strictly between $0$ and $1$, so a feature never seen in a
class does not rule the class out.

**Predict.** Score a test row $x$ against each class (natural log) and predict
the class with the highest score:

$$
\operatorname{score}_c(x) = \log \pi_c + \sum_{j=1}^{d} \Big[ x_j \log \theta_{cj} + (1 - x_j) \log\left(1 - \theta_{cj}\right) \Big]
$$

Unlike multinomial naive Bayes, an **absent** feature ($x_j = 0$) is evidence
too: it contributes $\log(1 - \theta_{cj})$. If two classes tie for the highest
score, predict the **smaller** label. (The tests never put two different
scores within a relative $10^{-9}$ of each other.)

**Return** the list of predicted labels, one per row of `XTest`.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

## Constraints

- `1 <= n <= 1000` training rows and `1 <= m <= 1000` test rows
- `1 <= d <= 200` features, the same in `X` and `XTest`; every value is `0` or `1`
- Labels are integers with absolute value `<= 10⁶`; at most `20` distinct labels
- `0 < alpha <= 10`

## Examples

**Example 1**
```
Input:  X = [[1, 0], [1, 1], [0, 1], [0, 0]], y = [1, 1, 0, 0], XTest = [[1, 0], [0, 1]], alpha = 1.0
Output: [1, 0]
Explanation: class 1 has θ = [(2 + 1)/4, (1 + 1)/4] = [0.75, 0.5] and class 0
has θ = [0.25, 0.5]. Feature 0 decides: [1, 0] scores log(0.5 · 0.75 · 0.5)
for class 1 against log(0.5 · 0.25 · 0.5) for class 0.
```

**Example 2**
```
Input:  X = [[1, 0, 0], [1, 0, 0], [0, 1, 1], [1, 1, 1], [0, 0, 1]], y = [5, 5, 3, 3, 3],
        XTest = [[1, 0, 1], [0, 0, 0], [1, 1, 0]], alpha = 1.0
Output: [3, 5, 5]
Explanation: class 5 (prior 2/5) has θ = [3/4, 1/4, 1/4] and class 3
(prior 3/5) has θ = [2/5, 3/5, 4/5]. For [0, 0, 0], class 5 scores
log(2/5 · 1/4 · 3/4 · 3/4) ≈ −2.878 and class 3 scores
log(3/5 · 3/5 · 2/5 · 1/5) ≈ −3.547, so class 5 wins. The three absent
features are what decide it: a model that skipped them would compare only the
priors and pick class 3.
```

**Example 3**
```
Input:  X = [[1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0]], y = [0, 0, 1], XTest = [[0, 0, 0, 0], [0, 0, 0, 1]],
        alpha = 0.5
Output: [0, 1]
Explanation: with alpha = 0.5 the denominators are n_c + 1, so class 0 has
θ = [5/6, 1/2, 1/6, 1/6] and class 1 has θ = [1/4, 1/4, 3/4, 1/4]. Feature 3 is
never 1 in training, yet its smoothed θ is 1/6 in class 0 against 1/4 in
class 1, which tips the second row to class 1.
```
