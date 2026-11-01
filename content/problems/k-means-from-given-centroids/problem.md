# K-Means from Given Centroids

**k-means** groups $N$ points into $K$ clusters, each represented by a
**centroid**. Implement **Lloyd's algorithm**, the standard way to run it,
starting from the centroids you're given:

```
repeat at most maxIters times:
    1. assign:  label every point with its nearest centroid
    2. if this is not the first assignment and no label changed: stop
    3. update:  move every centroid to the mean of the points labelled with it
```

One pass through steps 1–3 is one iteration. Every remaining choice is pinned,
so there is exactly one right answer:

- **Distance** is squared Euclidean:
  $\lVert p - c \rVert^2 = \sum_j (p_j - c_j)^2$.
- **Ties:** a point that is equally close to several centroids goes to the one
  with the **lowest index**.
- **Empty clusters:** a centroid that no point is labelled with **stays where it
  is**.
- **Stopping:** after `maxIters` iterations, or as soon as an assignment changes
  no label (step 2), whichever comes first.

**Return `[centroids, labels]`:**

- `centroids`: the final $K$ centroids in their original order, so centroid $k$
  is the one that started at `initialCentroids[k]`.
- `labels`: $N$ integers, where `labels[i]` is point $i$'s centroid in the
  **last assignment** (step 1). When the iterations run out, that is the
  assignment the final centroids were averaged from. Don't assign again after
  the last update.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays are fine as return values.

Exact ties do occur in the tests, so the tie rule matters. Near-ties do not:
the tests are built so that every correct way of computing the distances picks
the same centroid.

Centroids are accepted when every coordinate is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. Labels must match exactly.

## Constraints

- `1 <= N <= 200`, where `N = len(points)`
- `1 <= K <= 10`, where `K = len(initialCentroids)`
- Every point and every initial centroid has the same length `d`, with
  `1 <= d <= 10`
- Every coordinate is a finite number with absolute value `<= 100`
- `1 <= maxIters <= 100`
- Initial centroids need not be distinct, and `K` may exceed `N`

## Examples

**Example 1**
```
Input:  points = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0],
                  [3.0, 3.0], [4.0, 3.0], [3.0, 4.0], [2.0, 2.0]],
        initialCentroids = [[0.0, 0.0], [4.0, 4.0]],
        maxIters = 10
Output: [[[0.75, 0.75], [3.3333333333333335, 3.3333333333333335]],
         [0, 0, 0, 1, 1, 1, 0]]
Explanation: in the first assignment, [2, 2] is at squared distance 8 from
both centroids, so the tie sends it to centroid 0. The update moves centroid 0
to the mean of its four points, [0.75, 0.75], and centroid 1 to [10/3, 10/3].
The second assignment changes no label, so the algorithm stops.
```

**Example 2**
```
Input:  points = [[8.0, 4.0], [3.0, 7.0], [7.0, 0.0], [1.0, 0.0], [0.0, 8.0]],
        initialCentroids = [[5.0, 7.0], [4.0, 5.0]],
        maxIters = 1
Output: [[[3.0, 7.0], [4.0, 3.0]], [1, 0, 1, 1, 1]]
Explanation: only [3, 7] is closer to centroid 0 (squared distance 4 against
5), so centroid 0 moves to [3, 7] and centroid 1 to the mean of the other four
points, [4, 3]. That uses up maxIters. [0, 8] is now closer to centroid 0, but
no iteration is left to reassign it, so its label stays 1.
```

**Example 3**
```
Input:  points = [[0.0, 0.0], [2.0, 0.0], [0.0, 2.0], [2.0, 2.0],
                  [8.0, 8.0], [10.0, 8.0], [8.0, 10.0], [10.0, 10.0]],
        initialCentroids = [[12.0, 12.0], [0.0, 0.0], [12.0, 12.0]],
        maxIters = 10
Output: [[[9.0, 9.0], [1.0, 1.0], [12.0, 12.0]], [1, 1, 1, 1, 0, 0, 0, 0]]
Explanation: centroids 0 and 2 start at the same spot, so each of the four
points near [9, 9] is tied between them and goes to centroid 0. Centroid 2
never gets a point, so it stays at [12, 12]. The centroids come back in their
original order, not sorted.
```
