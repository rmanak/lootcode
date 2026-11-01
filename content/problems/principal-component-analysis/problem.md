# Principal Component Analysis

**Principal component analysis (PCA)** finds the directions along which a
dataset varies the most. They are the eigenvectors of the data's covariance
matrix, ranked by their eigenvalues, the variance along each direction.
Projecting onto the top few gives the best low-dimensional summary of the
data.

`X` holds $N$ points (rows) $x_i$ with $d$ features. Compute the top $k$
components exactly like this. Center every column on its mean $\mu$, then take
the sample covariance $\Sigma$, a $d \times d$ matrix:

$$
\begin{aligned}
\mu &= \frac{1}{N} \sum_{i=1}^{N} x_i \\
X_c &= X - \mu \\
\Sigma &= \frac{1}{N - 1}\, X_c^\top X_c
\end{aligned}
$$

Let $\lambda_1 > \lambda_2 > \dots > \lambda_k$ be the $k$ largest eigenvalues
of $\Sigma$, and $v_i$ the unit-length eigenvector for $\lambda_i$, so
$\Sigma v_i = \lambda_i v_i$ and $\lVert v_i \rVert = 1$.

An eigenvector is only defined up to its sign, so fix it: **flip $v_i$ if
needed so that its entry with the largest absolute value is positive.**

**Return `[components, projected, explainedVariance]`**:

- `components`: $k$ rows, row $i$ being $v_i$ ($d$ numbers), largest
  eigenvalue first;
- `projected`: $X_c V^\top$, where $V$ is `components`: the centered points in
  the new coordinates ($N$ rows of $k$ numbers);
- `explainedVariance`: $[\lambda_1, \dots, \lambda_k]$.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays are fine as return values.

The tests guarantee the answer is unique: the $k$ largest eigenvalues are well
separated from each other and from the next one, and in every component one
entry is clearly the largest in absolute value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `2 <= N <= 200` and `1 <= d <= 10`
- Every entry of `X` is a finite number with absolute value `<= 1000`
- `1 <= k <= d`
- The `min(k + 1, d)` largest eigenvalues of `Cov` differ from each other by at
  least `10⁻³ · λ₁`, and `λ₁ > 0`
- In each of the top `k` eigenvectors, the largest absolute entry exceeds the
  second largest by at least `10⁻⁶`

## Examples

**Example 1**
```
Input:  X = [[2.0, 0.0], [0.0, 1.0], [-2.0, 0.0], [0.0, -1.0]], k = 1
Output: [[[1.0, 0.0]], [[2.0], [0.0], [-2.0], [0.0]], [2.6666666666666665]]
Explanation: the data is already centered. Cov = [[8/3, 0], [0, 2/3]], so the
top direction is the x-axis with variance 8/3. Projecting keeps each point's x.
```

**Example 2**
```
Input:  X = [[1.0, 2.0], [3.0, 3.0], [5.0, 4.0], [2.0, 4.0], [4.0, 2.0]], k = 2
Output: [[[0.9570920264890529, 0.28978414868843005],
          [-0.28978414868843005, 0.9570920264890529]],
         [[-2.2039682016665356, -0.3775237291121928], [0.0, 0.0],
          [2.2039682016665356, 0.3775237291121928],
          [-0.6673078778006228, 1.246876175177483],
          [0.6673078778006228, -1.246876175177483]],
         [2.6513878188659974, 0.8486121811340027]]
Explanation: the mean is [3, 3], so the second point projects to the origin.
The second component's largest entry, 0.957, is positive, so it is kept as is
even though its first entry is negative.
```

**Example 3**
```
Input:  X = [[2.0, -3.0, -2.0], [-2.0, -2.0, 2.0], [3.0, 1.0, -3.0],
             [-3.0, -1.0, 0.0], [1.0, 0.0, -2.0]], k = 2
Output: [[[0.7740459300976565, 0.23144668410404856, -0.5893091977192398],
          [-0.34747434205319694, 0.9333773411870709, -0.08982383076473932]],
         [[1.5196985036869246, -2.402384667305157],
          [-3.702275323476613, -0.4384052809642556],
          [3.8088403679200153, 1.073474186154669],
          [-3.0662561740317407, 1.0220940638054907],
          [1.4399926259014135, 0.7452216983092527]],
         [10.499774187166862, 2.1790074408295093]]
```
