# Perceptron Learning Rule

The **perceptron** is the oldest linear classifier. It predicts $+1$ when
$w \cdot x + b > 0$ and $-1$ otherwise, and it learns by fixing its own
mistakes one example at a time. Train it exactly as follows.

`X` has $N$ rows (examples) $x_i$ of $d$ integer features, and `y` has the
labels $y_i$, each $+1$ or $-1$.

Start from $w = 0$ ($d$ zeros) and $b = 0$. One **epoch** visits the examples
$i = 0, 1, \dots, N - 1$ in their given order. Example $i$ is a **mistake**
when

$$
y_i\, (w \cdot x_i + b) \le 0
$$

(a score of exactly $0$ is a mistake), and every mistake immediately updates

$$
\begin{aligned}
w &\leftarrow w + y_i\, x_i \\
b &\leftarrow b + y_i
\end{aligned}
$$

At the end of each epoch, record how many mistakes it made. Stop after an
epoch with no mistakes (a clean pass: the data is separated), or after
`maxEpochs` epochs, whichever comes first.

With $w$ and $b$ starting at zero, the very first example is always a mistake.

**Return `[w, b, mistakesPerEpoch]`**:
- `w`: $d$ integers
- `b`: an integer
- `mistakesPerEpoch`: the count recorded for each epoch that ran

`mistakesPerEpoch` ends with `0` if the run stopped early. It has `maxEpochs`
entries if the data was never separated.

Everything here is integer arithmetic, so answers must match exactly.

## Constraints

- `1 <= N <= 200` and `1 <= d <= 10`, where `X` has `N` rows of `d` integers
- Every feature is an integer with absolute value `<= 100`
- `y` has `N` entries, each `1` or `-1`
- `1 <= maxEpochs <= 100`

## Examples

**Example 1**
```
Input:  X = [[2, 1], [-1, -1], [1, 3], [-2, 1]], y = [1, -1, 1, -1], maxEpochs = 10
Output: [[2, 1], 1, [1, 0]]
Explanation: the first example scores 0, which is a mistake, so w = [2, 1] and
b = 1. That line already classifies the other three examples correctly, and
the second epoch makes no mistakes, so training stops.
```

**Example 2**
```
Input:  X = [[0, 0], [1, 1]], y = [1, -1], maxEpochs = 5
Output: [[-1, -1], 1, [2, 1, 0]]
Explanation:
Epoch 1: example 0 scores 0, so b = 1. Example 1 scores −1 · (0 + 1) = −1, so w = [−1, −1] and b = 0.
Epoch 2: example 0 scores 0 again, so b = 1. Example 1 scores −1 · (−2 + 1) = 1, which is correct.
Epoch 3: no mistakes, so training stops.
```

**Example 3**
```
Input:  X = [[1], [-1], [2], [-2]], y = [1, 1, -1, -1], maxEpochs = 3
Output: [[0], 0, [4, 4, 4]]
Explanation: no line separates these labels. Every epoch makes 4 mistakes and
ends with w = [0] and b = 0, so all 3 epochs run.
```
