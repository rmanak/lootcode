A symmetric $2 \times 2$ matrix `[[a, b], [b, c]]`, that is

$$
\begin{pmatrix} a & b \\ b & c \end{pmatrix}
$$

has two real eigenvalues and orthogonal eigenvectors. It shows up everywhere:
as the covariance of 2-D points (the axes of an ellipse), as a structure
tensor in corner detection, and as one rotation step of the Jacobi eigenvalue
method. The closed form is short, but there are two traps. One is
**numerical**: the textbook quadratic formula loses the small eigenvalue to
cancellation when the two eigenvalues differ greatly in size. The other is
**convention**: an eigenvector is only defined up to sign.

For each matrix in `matrices`, return `[lambda1, lambda2, v1, v2]`:

- $\lambda_1 \ge \lambda_2$, the eigenvalues.
- $v_1$, a **unit** eigenvector for $\lambda_1$, with a **positive first
  component**. If its first component is 0, its second component is
  positive.
- `v2 = [-v1[1], v1[0]]`, which is $v_1$ turned 90° counter-clockwise (a unit
  eigenvector for $\lambda_2$).
- If the matrix is a multiple of the identity ($b = 0$ and $a = c$), every
  vector is an eigenvector. Use `v1 = [1, 0]` and `v2 = [0, 1]`.

Entries go up to $10^8$, while an eigenvalue can be as small as about
$10^{-6}$. Results must still be accurate to the tolerance below, so compute
the eigenvalues in a numerically stable way.

You may use the Python standard library and **numpy**. numpy's own
eigenvector signs are arbitrary, so you will have to normalize them.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. For every matrix with $b \ne 0$, the
two eigenvalues differ by at least `1e-6` times the larger magnitude, and
`v1[0] >= 1e-6`, so every answer is well defined.

## Constraints

- `1 <= len(matrices) <= 200`
- Each matrix is `[[a, b], [b, c]]`, exactly symmetric, with finite entries of
  absolute value `<= 10⁸`

## Examples

**Example 1**
```
Input:  matrices = [[[2.0, 1.0], [1.0, 2.0]], [[3.0, 0.0], [0.0, 5.0]], [[4.0, 0.0], [0.0, 4.0]]]
Output: [[3.0, 1.0, [0.7071067811865476, 0.7071067811865475], [-0.7071067811865475, 0.7071067811865476]],
         [5.0, 3.0, [0.0, 1.0], [-1.0, 0.0]],
         [4.0, 4.0, [1.0, 0.0], [0.0, 1.0]]]
Explanation: the first matrix has eigenvalues 3 and 1, with eigenvectors along
(1, 1) and (−1, 1). The second is diagonal, but the larger eigenvalue, 5,
belongs to the second axis. So v1 = [0, 1] (first component 0, second
positive), and v2 is [0, 1] turned counter-clockwise, [−1, 0]. The third is
4 · I.
```

**Example 2**
```
Input:  matrices = [[[1.0, -2.0], [-2.0, -2.0]], [[0.0, 1.0], [1.0, 0.0]]]
Output: [[2.0, -3.0, [0.8944271909999159, -0.4472135954999579], [0.4472135954999579, 0.8944271909999159]],
         [1.0, -1.0, [0.7071067811865476, 0.7071067811865475], [-0.7071067811865475, 0.7071067811865476]]]
Explanation: the trace is −1 and the determinant is −6, so the eigenvalues
are 2 and −3. The eigenvector for 2 is along (2, −1), normalized with its
first component positive.
```

**Example 3**
```
Input:  matrices = [[[-3.0, 4.0], [4.0, 3.0]], [[5.0, 2.0], [2.0, 2.0]]]
Output: [[5.0, -5.0, [0.44721359549995804, 0.8944271909999159], [-0.8944271909999159, 0.44721359549995804]],
         [6.0, 1.0, [0.8944271909999159, 0.4472135954999579], [-0.4472135954999579, 0.8944271909999159]]]
Explanation: in the first matrix a < c, and the eigenvector for 5 is along
(1, 2). An angle formula that can't tell which quadrant it is in (atan of
2b/(a − c) instead of atan2) lands on the other eigenvector.
```
