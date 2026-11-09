A lidar scan of a street is mostly road: in a typical frame about 70% of the
3-D points lie on one plane, and the rest are cars, poles and noise. Finding
that dominant plane is a classic use of **RANSAC**: fit a plane to a few
random points, count how many points agree with it, keep the best, and refit
on its agreeing points.

`points` is a list of $n$ points $[x, y, z]$.

**Part 1: distances.** `plane` is $[a, b, c, d]$, the plane
$ax + by + cz + d = 0$. Its normal $(a, b, c)$ need not be a unit vector. The
distance of a point $p$ from it is

$$
\operatorname{dist}(p) = \frac{|a p_x + b p_y + c p_z + d|}{\sqrt{a^2 + b^2 + c^2}}
$$

**Part 2: RANSAC.** The random choices are given: `triples` lists the
candidate samples, each three indices into `points`.

1. For each triple, in order, take the plane through its three points (its
   normal is the cross product of two edge vectors). Its **inliers** are the
   points at distance $\le$ `threshold` from that plane. Keep the triple with
   the **most** inliers; on a tie, the earliest triple.
2. **Refit** a plane to the winning triple's inliers by **total least
   squares**: it passes through their centroid $\mu$, and its normal is the
   direction in which the centered inliers vary least, the right singular
   vector of the smallest singular value of the matrix whose rows are
   $p - \mu$. (Total least squares measures perpendicular distance. Ordinary
   least squares, fitting $z$ as a function of $x$ and $y$, does not.)
3. The **outliers** are the points at distance $>$ `threshold` from the refitted
   plane.

**Return `[distances, outliers, refitDistances]`**: the $n$ part-1 distances,
the indices of the outliers in increasing order, and the $n$ distances from
the refitted plane.

The tests promise that no triple is collinear, that every distance used in a
comparison is at least $10^{-6}$ away from `threshold`, and that the winning
triple's inliers are not all on one line.

You may use **numpy** and the Python standard library.

## Constraints

- `4 <= n <= 2000`; every coordinate is finite with absolute value `<= 1000`
- `plane` has `4` finite numbers, and `(a, b, c)` is not the zero vector
- `1 <= len(triples) <= 200`; each triple holds 3 distinct indices in `[0, n)`
- `0 < threshold <= 100`

## Examples

**Example 1**
```
Input:  points = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 5.0]],
        plane = [0.0, 0.0, 2.0, -2.0], triples = [[0, 1, 4], [0, 1, 2]], threshold = 0.1
Output: [[1.0, 1.0, 1.0, 1.0, 4.0], [4], [0.0, 0.0, 0.0, 0.0, 5.0]]
Explanation: 2z − 2 = 0 is the plane z = 1 (the normal's length 2 is divided
out). The first triple spans the plane y = 0, which holds points 0, 1 and 4;
the second spans z = 0, which holds four points and wins. Refitting on those
four gives z = 0 again, and point 4 is the outlier.
```

**Example 2**
```
Input:  points = [[0.0, 0.0, 0.02], [2.0, 0.0, -0.02], [0.0, 2.0, -0.02], [2.0, 2.0, 0.02], [1.0, 1.0, 3.0],
                  [1.0, 0.0, 2.5]],
        plane = [1.0, 1.0, 1.0, 0.0], triples = [[0, 4, 5], [0, 1, 2], [1, 2, 3]], threshold = 0.15
Output: [[0.011547005383792516, 1.143153532995459, 1.143153532995459, 2.3209480821422956, 2.886751345948129,
          2.0207259421636903],
         [4, 5],
         [0.02, 0.02, 0.02, 0.02, 3.0, 2.5]]
Explanation: the plane through points 0, 1 and 2 is slightly tilted, but point
3 is within 0.15 of it, so that triple has 4 inliers against 3 for the first.
The four ground points sit 0.02 above and below z = 0, and the total least
squares fit through them is exactly z = 0.
```

**Example 3**
```
Input:  points = [[0.0, 0.0, 0.0], [4.0, 0.0, 1.0], [0.0, 4.0, 0.0], [4.0, 4.0, 1.0], [2.0, 2.0, 0.6], [2.0, 2.0, 4.0]],
        plane = [0.0, 0.0, 1.0, 0.0], triples = [[0, 1, 2], [1, 2, 3], [0, 2, 5]], threshold = 0.3
Output: [[0.0, 1.0, 0.0, 1.0, 0.6, 4.0],
         [5],
         [0.019173948916013654, 0.019630676199284162, 0.019173948916013654, 0.019630676199284162,
          0.07760925023059578, 3.3760023850309158]]
Explanation: the first triple spans the tilted plane z = x/4, and point 4 is
0.1 above it (a perpendicular distance of about 0.097), so it is an inlier
too. The refit through all five inliers is pulled slightly toward point 4, so
no point lies exactly on it.
```
