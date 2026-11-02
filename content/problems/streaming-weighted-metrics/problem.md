Evaluation loops see the data in batches, and the dataset may not fit in
memory. Implement a metric object that accumulates **weighted** binary
classification metrics batch by batch, like the stateful metrics in Keras or
TorchMetrics.

Implement the `WeightedMetrics` class:

- `WeightedMetrics(threshold)`: a new, empty accumulator. An example is
  predicted positive when its probability is `>= threshold`.
- `update(scores, labels, weights)`: add a batch. `scores[i]` is the predicted
  probability that example `i` is positive, `labels[i]` is its true label (`0`
  or `1`), and `weights[i] >= 0` is how much it counts. Returns nothing.
- `result()`: return `[accuracy, precision, recall, logLoss]` over **every
  example added since the object was created or last reset**. Calling it does
  not change the state.
- `reset()`: forget everything added so far. Returns nothing.

Count with weights: $\texttt{tp}$ is the total weight of the true positives,
and so on, and $W$ is the total weight of all examples. For every example $i$
added, write $p_i$ for its score, $y_i$ for its label and $w_i$ for its
weight. Then

$$
\begin{aligned}
\text{accuracy} &= \frac{\texttt{tp} + \texttt{tn}}{W} \\[1ex]
\text{precision} &= \frac{\texttt{tp}}{\texttt{tp} + \texttt{fp}} \\[1ex]
\text{recall} &= \frac{\texttt{tp}}{\texttt{tp} + \texttt{fn}} \\[1ex]
\text{logLoss} &= \frac{1}{W} \sum_i w_i\, \ell_i
\end{aligned}
$$

where each example's loss is

$$
\ell_i =
\begin{cases}
-\log p_i & \text{if } y_i = 1 \\
-\log (1 - p_i) & \text{if } y_i = 0
\end{cases}
$$

Any value that would be $0 / 0$ is $0$, including `result()` before any data.

The metrics must be computed from the totals over all batches. Averaging the
per-batch metrics gives different, wrong numbers when batches differ in size
or weight.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `0 <= threshold <= 1`
- Every score is a finite number in `[1e-6, 1 − 1e-6]`, so no logarithm is
  infinite
- Every label is `0` or `1`, and every weight is a finite number in `[0, 100]`
- Each `update` batch has between `1` and `1000` examples, at most `10⁵` in
  total
- At most `2000` operations in total

## Examples

**Example 1**
```
Input:  ["WeightedMetrics", "update", "result", "update", "result"]
        [[0.5], [[0.9, 0.4, 0.7], [1, 0, 0], [1.0, 2.0, 1.0]], [],
         [[0.2, 0.6], [1, 1], [0.5, 0.5]], []]
Output: [null, null, [0.75, 0.5, 1.0, 0.5827461418789359],
         null, [0.7, 0.6, 0.75, 0.6782232671231578]]
Explanation: the first batch predicts [1, 0, 1]: tp = 1, tn = 2 (one example
of weight 2), fp = 1, W = 4. The second batch adds fn = 0.5 and tp = 0.5. Over
both batches tp = 1.5, fp = 1, fn = 0.5, tn = 2 and W = 5, so accuracy is
3.5 / 5 = 0.7. Averaging the two batches' accuracies would give
(0.75 + 0.5) / 2 instead.
```

**Example 2**
```
Input:  ["WeightedMetrics", "result", "update", "result", "reset", "result"]
        [[0.5], [], [[0.5, 0.25], [1, 0], [2.0, 0.0]], [], [], []]
Output: [null, [0.0, 0.0, 0.0, 0.0], null, [1.0, 1.0, 1.0, 0.6931471805599453],
         null, [0.0, 0.0, 0.0, 0.0]]
Explanation: with no data every metric is 0 / 0 = 0. A score of 0.5 equals the
threshold, so it is predicted positive. The second example has weight 0, so it
counts for nothing. After reset() the object is empty again.
```

**Example 3**
```
Input:  ["WeightedMetrics", "update", "update", "result"]
        [[0.3], [[0.2, 0.8], [0, 1], [1.0, 1.0]], [[0.3], [0], [4.0]], []]
Output: [null, null, null, [0.3333333333333333, 0.2, 1.0, 0.3121644797305582]]
```
