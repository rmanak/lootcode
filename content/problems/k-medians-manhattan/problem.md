A ride-sharing app wants $K$ shuttle pickup points for $N$ riders on a city
grid. Riders walk along streets, so the cost of a rider is the **Manhattan
(L1) distance** to their nearest pickup point, and the goal is a small total
cost. This is the **k-medians** objective, and the standard heuristic is
Lloyd's algorithm with the mean replaced by the **median**: for a fixed group
of riders, the coordinate-wise median minimizes the total L1 distance.

Run it from the given starting centers:

```
repeat at most maxIters times:
    1. assign:  label every point with its nearest center (L1 distance)
    2. if this is not the first assignment and no label changed: stop
    3. update:  move every center to the coordinate-wise median of its points
```

with every remaining choice pinned:

- **Distance:** $\lVert p - c \rVert_1 = \sum_j |p_j - c_j|$.
- **Ties:** a point equally close to several centers goes to the one with the
  **lowest index**.
- **Median:** sort the group's values in each coordinate separately. With an
  odd count take the middle one; with an even count take the **average of the
  two middle values** (what `numpy.median` does).
- **Empty clusters:** a center with no points **stays where it is**.

**Return `[centers, labels, cost]`:**

- `centers`: the final $K$ centers, in their original order.
- `labels`: each point's center in the **last assignment** (step 1).
- `cost`: $\sum_i \lVert p_i - \texttt{centers}[\texttt{labels}_i] \rVert_1$,
  measured against the final centers.

You may use **numpy** and the Python standard library.

## Constraints

- `1 <= N <= 2000`, `1 <= K <= 20`, `1 <= d <= 4` coordinates per point
- Point coordinates are integers with absolute value `<= 10⁴`
- `initialCenters` has `K` rows of `d` numbers, each a multiple of `0.5` with
  absolute value `<= 10⁴`
- `1 <= maxIters <= 100`

## Examples

**Example 1**
```
Input:  points = [[0, 0], [1, 0], [10, 0], [5, 3], [0, 8], [2, 9], [9, 9]],
        initialCenters = [[0.0, 0.0], [5.0, 9.0]], maxIters = 10
Output: [[[3.0, 0.0], [2.0, 9.0]], [0, 0, 0, 0, 1, 1, 1], 27.0]
Explanation: the first assignment puts the bottom three points with center 0
and the rest with center 1, whose x values 0, 2, 5, 9 have median 3.5 and whose
y values 3, 8, 9, 9 have median 8.5. In the second assignment (5, 3) is 7 from
both [1, 0] and [3.5, 8.5]; the tie sends it to center 0. The third assignment
changes nothing, so the algorithm stops. The cost is 17 for center 0 and 10 for
center 1.
```

**Example 2**
```
Input:  points = [[0, 0], [1, 1], [2, 2], [5, 3], [100, 100]],
        initialCenters = [[0.0, 0.0], [5.0, 9.0]], maxIters = 1
Output: [[[1.0, 1.0], [52.5, 51.5]], [0, 0, 0, 1, 1], 196.0]
Explanation: one iteration. (5, 3) is 8 from [0, 0] and 6 from [5, 9] in L1,
so it joins center 1 (in squared Euclidean distance it would be the other way
round, 34 against 36). Center 1's group is (5, 3) and (100, 100): two values
per coordinate, so the medians are the averages 52.5 and 51.5.
```

**Example 3**
```
Input:  points = [[0], [2], [5], [10], [11]], initialCenters = [[3.0], [7.0], [50.0]], maxIters = 1
Output: [[[2.0], [10.5], [50.0]], [0, 0, 0, 1, 1], 6.0]
Explanation: 5 is 2 from both 3 and 7, and the tie goes to center 0. No point
is nearest to 50, so that center stays put.
```
