**Multinomial naive Bayes** is the classic text classifier. It describes each
document as a bag of word counts and assumes the words are drawn independently
given the class. Train it on labelled documents and classify new ones.

`trainX` has $N$ documents, each a row of $V$ word counts (`trainX[n][j]` is
how many times word $j$ appears in document $n$). `trainY[n]` is that
document's class. The classes are $0, 1, \dots, C - 1$, where
$C$ = `max(trainY) + 1`, and every class appears in `trainY` at least once.
`testX` holds $M$ documents to classify, in the same format.

**Training.** For each class $c$, let $N_c$ be the number of training documents
of class $c$, $n_{cj}$ the total count of word $j$ over those documents, and
$n_c = \sum_j n_{cj}$. With $\alpha$ = `alpha`, the prior $\pi_c$ and the
word probabilities $\theta_{cj}$ (Laplace / Lidstone smoothing) are

$$
\begin{aligned}
\pi_c &= \frac{N_c}{N} \\
\theta_{cj} &= \frac{n_{cj} + \alpha}{n_c + \alpha V}
\end{aligned}
$$

The smoothing is added to every word of the vocabulary, so the denominator
gets $\alpha V$. The prior is **not** smoothed.

**Classifying** a document $x$ (a row of $V$ counts $x_j$): its joint
log-probability $J_c$ with each class, and its log-posterior, are

$$
\begin{aligned}
J_c &= \log \pi_c + \sum_{j=1}^{V} x_j \log \theta_{cj} \\
\log P(c \mid x) &= J_c - \log \sum_{k=0}^{C-1} e^{J_k}
\end{aligned}
$$

The prediction is the class with the largest $J_c$, and the smallest such class
on a tie.

**Return `[predictions, logPosteriors]`**:
- `predictions`: $M$ integers
- `logPosteriors`: $M$ rows of $C$ numbers, $\log P(c \mid x)$ for
  $c = 0, \dots, C - 1$. Each row is normalized, so the exponentials of its
  entries sum to $1$.

**Numerical stability matters.** A long document can give every class a joint
log-probability $J_c < -745$. $e^{J_c}$ is then exactly $0$ in floating point,
and normalizing naively gives $0 / 0$. Use log-sum-exp.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

The predictions must match exactly. A log-posterior is accepted when it is
within a relative `1e-6` (or an absolute `1e-9`) of the expected value. In the
tests, the top two joint values of a document are either more than `1e-6`
apart, or exactly tied because the two classes have identical data.

## Constraints

- `1 <= N <= 200`, `1 <= M <= 100` and `1 <= V <= 50`
- Every count is an integer in `[0, 100]`
- Each `trainY[n]` is an integer in `[0, 9]`, and every class from `0` to
  `max(trainY)` appears at least once
- `0 < alpha <= 10`

## Examples

**Example 1**
```
Input:  trainX = [[2, 1, 0], [3, 0, 1], [0, 2, 3], [1, 0, 4]], trainY = [0, 0, 1, 1],
        testX = [[1, 1, 0], [0, 0, 2]], alpha = 1.0
Output: [[0, 1], [[-0.2591730148934275, -1.477048724388354],
                  [-2.3482709792367116, -0.10041078593191277]]]
Explanation: class 0's counts are [5, 1, 1] (total 7) and class 1's are
[1, 2, 7] (total 10). With alpha = 1 and V = 3, θ(0) = [6, 2, 2] / 10 and
θ(1) = [2, 3, 8] / 13. The first document uses words 0 and 1, which favour
class 0. The second uses word 2 twice, which favours class 1.
```

**Example 2**
```
Input:  trainX = [[1, 0], [0, 1], [1, 1]], trainY = [0, 1, 2], testX = [[0, 0], [5, 0]],
        alpha = 0.5
Output: [[0, 0], [[-1.0986122886681098, -1.0986122886681098, -1.0986122886681098],
                  [-0.12733942237660134, -5.6204008657171505, -2.1546649629174244]]]
Explanation: the empty document has no words, so only the priors count. All
three are 1/3, so it is a three-way tie, and the smallest class, 0, wins.
```

**Example 3**
```
Input:  trainX = [[4, 0, 0], [0, 4, 0], [1, 0, 3]], trainY = [1, 0, 1], testX = [[2, 2, 0]],
        alpha = 1.0
Output: [[0], [[-0.38682282094888176, -1.1369730217732563]]]
Explanation: class 1 has twice the prior of class 0. But word 1 appears only
in class 0's training document, and under class 1 its smoothed probability is
just 1/11. Class 0 wins.
```
