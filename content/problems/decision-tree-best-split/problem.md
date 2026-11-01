# Decision Tree: Best Gini Split

A decision tree grows by repeatedly splitting a node's examples in two with a
question of the form "is feature $j$ at most $t$?". CART-style trees pick the
question that most reduces the **Gini impurity**. Find that best split for one
node.

`X` holds $N$ examples (rows) with $d$ numeric features, and `y` their class
labels. The Gini impurity of a set $S$ of examples, where $p_c$ is the fraction
of $S$ with label $c$, is

$$
G(S) = 1 - \sum_c p_c^2
$$

**Candidate splits.** For each feature $j$, sort the distinct values it takes;
every **midpoint** between two consecutive distinct values $a < b$ is a
candidate threshold $t = (a + b) / 2$. The split sends the examples with
`X[i][j] <= t` to the left child $L$ and the rest to the right child $R$. A
feature with only one distinct value has no candidates.

**Gain.** A split's gain is the drop from the node's impurity to the children's
size-weighted impurity:

$$
\text{gain} = G(\text{node}) - \frac{|L|}{N}\, G(L) - \frac{|R|}{N}\, G(R)
$$

**Return `[feature, threshold, gain]`** for the candidate with the **largest
gain**. Break ties by the **lowest feature index**, then the **lowest
threshold**. Two gains that differ by less than `1e-9` count as tied: equal
fractions can come out a few units apart in the last digit after floating-point
rounding.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists.

The threshold and the gain are accepted when they are within a relative `1e-6`
(or an absolute `1e-9`) of the expected values. The feature must match exactly.
In every test, any gain that is not tied with the best trails it by more than
`1e-6`.

## Constraints

- `2 <= N <= 500` and `1 <= d <= 10`
- Every entry of `X` is a finite number with absolute value `<= 10⁴`
- `y` has `N` entries, each an integer with `0 <= y[i] <= 9`
- At least one feature takes two or more distinct values

## Examples

**Example 1**
```
Input:  X = [[2.0], [3.0], [10.0], [19.0]], y = [0, 0, 1, 1]
Output: [0, 6.5, 0.5]
Explanation: the candidates are 2.5, 6.5 and 14.5. Splitting at 6.5 separates
the classes perfectly: both children are pure, so the gain is the node's whole
impurity, 1 − (½² + ½²) = 0.5. The other two thresholds gain only 1/6.
```

**Example 2**
```
Input:  X = [[1.0, 5.0], [2.0, 6.0], [3.0, 7.0], [4.0, 8.0]], y = [0, 1, 0, 1]
Output: [0, 1.5, 0.16666666666666669]
Explanation: four candidates tie at a gain of 1/6: thresholds 1.5 and 3.5 on
feature 0, and 5.5 and 7.5 on feature 1. The lowest feature, then the lowest
threshold, wins.
```

**Example 3**
```
Input:  X = [[1.0, 0.0], [1.0, 0.0], [2.0, 1.0], [3.0, 1.0], [3.0, 0.0], [4.0, 1.0]],
        y = [0, 0, 1, 2, 2, 2]
Output: [0, 2.5, 0.38888888888888895]
Explanation: feature 0 takes the values 1, 2, 3 and 4, so its candidates are
1.5, 2.5 and 3.5; feature 1 has one candidate, 0.5. At 2.5, the left child
holds labels {0, 0, 1} and the right child {2, 2, 2}.
```
