# Bilinear Image Resize

Every vision pipeline resizes images, and "bilinear" means slightly different
things in different libraries. That is how the same model gives different
results in training and in production. Implement bilinear resizing exactly as
PyTorch's `F.interpolate(mode="bilinear")` does, for a single-channel image,
in both of its `align_corners` modes.

**Source coordinates.** Each output index $d$ along an axis (input length
$n_\text{in}$, output length $n_\text{out}$) maps to a fractional input
coordinate $s$:

- `alignCorners = false` (the default; pixel centers sit at half-integers):
  $s = (d + 0.5)\, n_\text{in} / n_\text{out} - 0.5$, then **clamped below at
  0**: $s \leftarrow \max(s, 0)$.
- `alignCorners = true` (the corner pixels line up exactly):
  $s = d\, (n_\text{in} - 1) / (n_\text{out} - 1)$, or $s = 0$ when
  $n_\text{out} = 1$.

**Interpolation.** Along that axis, with

$$
\begin{aligned}
i_0 &= \lfloor s \rfloor \\
i_1 &= \min(i_0 + 1,\; n_\text{in} - 1) \\
\lambda &= s - i_0
\end{aligned}
$$

the 1-D interpolation of the values $v$ is
$(1 - \lambda)\, v_{i_0} + \lambda\, v_{i_1}$. Near the far edge $i_1$ stays at
the last pixel. Bilinear resizing does this along the columns and along the
rows, so an output pixel is a weighted average of the (up to) four input
pixels around $(s_\text{row}, s_\text{col})$, with weights
$(1 - \lambda_\text{row})(1 - \lambda_\text{col})$,
$(1 - \lambda_\text{row})\, \lambda_\text{col}$,
$\lambda_\text{row} (1 - \lambda_\text{col})$ and
$\lambda_\text{row}\, \lambda_\text{col}$.

**Return the `outHeight × outWidth` image**.

You may use the Python standard library and **numpy**. A numpy array is fine
as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `image` is `H × W` with `1 <= H, W <= 64`, and every pixel is a number in
  `[0, 255]`
- `1 <= outHeight, outWidth <= 64`
- `alignCorners` is a boolean

## Examples

**Example 1**
```
Input:  image = [[0.0, 100.0]], outHeight = 1, outWidth = 4, alignCorners = false
Output: [[0.0, 25.0, 75.0, 100.0]]
Explanation: the column coordinates are (d + 0.5) · 2/4 − 0.5 = −0.25, 0.25,
0.75 and 1.25. The first is clamped to 0, and the last has i0 = i1 = 1, so
it is 100.
```

**Example 2**
```
Input:  image = [[0.0, 100.0]], outHeight = 1, outWidth = 4, alignCorners = true
Output: [[0.0, 33.33333333333333, 66.66666666666666, 100.0]]
Explanation: s = d · 1/3, so the two end pixels land exactly on the input's
two pixels and the middle ones are evenly spaced.
```

**Example 3**
```
Input:  image = [[0.0, 40.0], [80.0, 120.0]], outHeight = 3, outWidth = 3, alignCorners = false
Output: [[0.0, 20.0, 40.0], [40.0, 60.0, 80.0], [80.0, 100.0, 120.0]]
Explanation: along each axis s = (d + 0.5) · 2/3 − 0.5 = −1/6, 1/2 and 7/6,
which become 0 (clamped), 0.5 and the last pixel.
```
