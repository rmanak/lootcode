# k-Nearest Neighbors Classifier

The **k-nearest neighbors** classifier has no training step. To label a new
point, it finds the `k` training points closest to it and takes a **majority
vote** of their labels.

You get $N$ labelled training points (`trainX`, `trainY`) and $M$ test points
(`testX`), all with $d$ coordinates. For every test point, independently:

1. Measure its distance to every training point $b$ with the **squared
   Euclidean distance**, $\sum_j (a_j - b_j)^2$, where $a$ is the test point.
2. Take the `k` nearest training points. If several training points are equally
   far away, the one with the **lower index** in `trainX` counts as nearer.
3. Predict the label that appears most often among those `k`. If several labels
   tie for the most votes, predict the **smallest** of them.

**Return the $M$ predicted labels**, in the order of `testX`.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists.

## Constraints

- `1 <= N <= 1000` and `1 <= M <= 200`
- `1 <= d <= 20`, and every point in `trainX` and `testX` has exactly `d`
  coordinates
- Every coordinate is a finite number with absolute value `<= 1000`
- `trainY` has `N` entries, each an integer with `0 <= label <= 100`
- `1 <= k <= N`

## Examples

**Example 1**
```
Input:  trainX = [[0, 0], [1, 0], [0, 1], [5, 5], [6, 5], [5, 6]],
        trainY = [0, 0, 0, 1, 1, 1],
        testX = [[0.5, 0.5], [5.2, 5.1], [2.5, 3.0]], k = 3
Output: [0, 1, 0]
Explanation: the first two test points sit inside a cluster and get its label.
The third is 10.25 from both [0, 1] (label 0) and [5, 5] (label 1), and 11.25
from [1, 0] (label 0), so its neighbours vote 0, 1, 0.
```

**Example 2**
```
Input:  trainX = [[0], [2], [-2], [5]], trainY = [1, 0, 2, 0],
        testX = [[0], [4]], k = 2
Output: [0, 0]
Explanation: for the test point 0, the nearest training point is 0 (label 1).
Points 2 and −2 tie for second place at distance 4, so index 1 (label 0) is
taken. The labels 1 and 0 then tie with one vote each, and the smaller, 0, wins.
For the test point 4, the two nearest are 5 and 2, both labelled 0.
```

**Example 3**
```
Input:  trainX = [[3, 0], [2, 2], [-2, -2], [0, 3], [0, -3]],
        trainY = [0, 1, 1, 0, 0],
        testX = [[0, 0], [2.5, 1.0]], k = 3
Output: [1, 0]
Explanation: from [0, 0], the points [2, 2] and [−2, −2] are at squared
distance 8, nearer than the other three at 9 (index 0 is taken among those),
so the vote is 1, 1, 0.
```
