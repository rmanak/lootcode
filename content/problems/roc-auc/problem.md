A binary classifier gives each example a **score**, where higher means "more
likely positive". **ROC-AUC** measures how well the scores rank positives above
negatives, without picking any threshold. It is the probability that a randomly
chosen positive scores higher than a randomly chosen negative, with a **tie
counting as half**. With $s$ = `scores`, $P$ the number of positives and $Q$
the number of negatives:

$$
\text{AUC} = \frac{1}{PQ} \sum_{\substack{i \text{ positive} \\ j \text{ negative}}} c_{ij}
$$

where each pair contributes

$$
c_{ij} =
\begin{cases}
1 & \text{if } s_i > s_j \\
\tfrac{1}{2} & \text{if } s_i = s_j \\
0 & \text{if } s_i < s_j
\end{cases}
$$

This equals the area under the ROC curve (the true-positive rate plotted against
the false-positive rate as the threshold sweeps from high to low), which is
where the name comes from.

Given `scores` and `labels` (`1` = positive, `0` = negative), **return the
AUC**.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy scalar is fine as the return value.

The tests include $N = 5 \cdot 10^4$ examples, many with tied scores, and each
test has a **2-second** time limit. Comparing every positive with every
negative is then over $6 \cdot 10^8$ comparisons, far too slow in plain Python.

Answers are accepted when they are within a relative `1e-6` (or an absolute
`1e-9`) of the expected value.

## Constraints

- `2 <= N <= 5·10⁴`, where `N = len(scores) = len(labels)`
- Every score is a finite number with absolute value `<= 10⁶`
- Each `labels[i]` is `0` or `1`, and both values occur at least once

## Examples

**Example 1**
```
Input:  scores = [0.2, 0.36, 0.37, 0.9, 0.6], labels = [0, 1, 0, 1, 0]
Output: 0.6666666666666666
Explanation: the positives score 0.36 and 0.9, and the negatives 0.2, 0.37
and 0.6. The positive at 0.36 beats only the negative at 0.2; the positive at
0.9 beats all three. That is 4 of the 6 pairs.
```

**Example 2**
```
Input:  scores = [0.7, 0.7, 0.3, 0.3, 0.9, 0.1], labels = [1, 0, 1, 0, 1, 0]
Output: 0.7777777777777778
Explanation: the positive at 0.7 ties the negative at 0.7 (1/2) and beats the
other two (2.5 in all). The positive at 0.3 loses to 0.7, ties 0.3 and beats
0.1 (1.5). The positive at 0.9 beats all three (3). That is 7 out of 9.
```

**Example 3**
```
Input:  scores = [2.0, 2.0, 2.0, 2.0], labels = [1, 0, 0, 1]
Output: 0.5
Explanation: every pair is tied, so every pair counts 1/2. A classifier that
can't tell the classes apart scores exactly 0.5, chance level.
```
