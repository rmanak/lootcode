To run a model in 8-bit integers, every float tensor is mapped onto the 256
values $-128, \dots, 127$. **Affine quantization** picks a scale $s$ and an
integer zero point $z$ so that a real value $r$ is stored as roughly
$r / s + z$. The parameters come from a **calibration** tensor, and are then
applied to other values, which may fall outside the calibrated range.

**Calibrate** on `calibration`, written $c$. The range always includes $0$:

$$
\begin{aligned}
r_\text{min} &= \min\left(\min_k c_k,\; 0\right) \\
r_\text{max} &= \max\left(\max_k c_k,\; 0\right) \\
s &= \frac{r_\text{max} - r_\text{min}}{255} \\
z &= \operatorname{clip}\left(\operatorname{round}\left(-128 - \frac{r_\text{min}}{s}\right),\, -128,\, 127\right)
\end{aligned}
$$

$s$ is `scale` (if it comes out as $0$, use $s = 1$) and $z$ is `zeroPoint`.
Including $0$ in the range means the real value $0.0$ (zero padding, or a ReLU
output) is stored exactly, as $z$.

**Quantize** each value $v$ of `x` to $q$, then **dequantize** it back to
$\hat v$ (`dequantized`):

$$
\begin{aligned}
q &= \operatorname{clip}\left(\operatorname{round}(v / s) + z,\; -128,\; 127\right) \\
\hat v &= (q - z)\, s
\end{aligned}
$$

$\operatorname{clip}(a, \mathit{lo}, \mathit{hi})$ clamps $a$ into
$[\mathit{lo}, \mathit{hi}]$. Values outside the calibrated range saturate at
$-128$ or $127$.

**Rounding is round-half-to-even**: a value exactly halfway between two
integers goes to the even one. So `0.5 → 0`, `1.5 → 2`, `2.5 → 2` and
`−1.5 → −2`. Python's built-in `round` and `numpy.rint` both do this.
`int(v + 0.5)` and `math.floor(v + 0.5)` do not.

**Return `[scale, zeroPoint, q, dequantized]`**, where `zeroPoint` and the
entries of `q` are integers.

You may use the Python standard library and **numpy**. Numpy arrays and numpy
scalars are fine as return values.

Integers must match exactly. Floats are accepted when every number is within a
relative `1e-6` (or an absolute `1e-9`) of the expected value. The tests never
put a value of $v / s$, or of $-128 - r_\text{min} / s$, within `1e-6` of a
halfway point unless it is exactly halfway. Exact ties use a power-of-two
scale, so floating-point division computes them exactly.

## Constraints

- `1 <= len(calibration), len(x) <= 10⁴`
- Every value is finite with absolute value `<= 10⁴`

## Examples

**Example 1**
```
Input:  calibration = [-64.0, 191.0], x = [0.5, 1.5, 2.5, -0.5, -1.5, 200.0, -70.0]
Output: [1.0, -64, [-64, -62, -62, -64, -66, 127, -128], [0.0, 2.0, 2.0, 0.0, -2.0, 191.0, -64.0]]
Explanation: scale = 255 / 255 = 1 and zeroPoint = −128 + 64 = −64. The first
five values are exact ties: 0.5 → 0, 1.5 → 2, 2.5 → 2, −0.5 → 0 and
−1.5 → −2. 200 lies above the calibrated range, so it saturates at 127, and
−70 saturates at −128.
```

**Example 2**
```
Input:  calibration = [0.5, 2.0, 3.0], x = [0.0, 1.0, 3.0, 2.2, -1.0]
Output: [0.011764705882352941, -128, [-128, -43, 127, 59, -128], [0.0, 1.0, 3.0, 2.2, 0.0]]
Explanation: the calibration values are all positive, but rmin is still 0, so
scale = 3 / 255 and 0.0 maps to q = −128 exactly.
```

**Example 3**
```
Input:  calibration = [-2.5, 0.75, 4.0], x = [-2.5, 0.0, 1.0, 4.0, 5.0]
Output: [0.025490196078431372, -30, [-128, -30, 9, 127, 127],
         [-2.4980392156862745, 0.0, 0.9941176470588236, 4.0019607843137255, 4.0019607843137255]]
Explanation: −128 − rmin / scale = −128 + 98.08 = −29.92, which rounds to
zeroPoint = −30. Because the zero point was rounded, the calibration endpoints
come back slightly off: −2.4980 and 4.0020.
```
