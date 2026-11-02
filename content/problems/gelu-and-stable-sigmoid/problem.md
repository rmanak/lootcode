Activation functions look trivial until an input is large. For every value $x$
in `x`, compute five things:

1. **sigmoid** $\sigma(x) = 1 / (1 + e^{-x})$
2. **its derivative** $\sigma(x)\,(1 - \sigma(x))$
3. **log-sigmoid** $\log \sigma(x)$
4. **GELU**, the activation used in BERT and GPT:
   $\operatorname{GELU}(x) = x\, \Phi(x)$, where
   $\Phi(x) = \tfrac{1}{2} \left(1 + \operatorname{erf}(x / \sqrt{2})\right)$ is
   the standard normal CDF. Use this **exact** form, not the `tanh`
   approximation.
5. **its derivative** $\Phi(x) + x\, \varphi(x)$, where
   $\varphi(x) = e^{-x^2/2} / \sqrt{2\pi}$ is the standard normal density

**Return `[sigmoid, sigmoidGrad, logSigmoid, gelu, geluGrad]`**, five lists
each as long as `x`.

**Stability.** Inputs go up to $\pm 1000$:
- `math.exp(1000)` raises `OverflowError`, so never exponentiate a large
  positive number. For $x < 0$, use $\sigma(x) = e^x / (1 + e^x)$.
- For $x = -800$, $\sigma(x)$ underflows to exactly $0$, so `log(σ(x))` is
  `-inf`. The true value is about $-800$. Compute log-sigmoid directly:
  $\log \sigma(x) = -\log(1 + e^{-x})$ for $x \ge 0$, and
  $x - \log(1 + e^{x})$ for $x < 0$. `math.log1p` keeps the small cases
  accurate.

You may use **numpy** and the Python standard library (`math.erf` is there).
Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. `-0.0` and `0.0` are equal.

## Constraints

- `1 <= len(x) <= 10⁴`
- Every value is a finite number with absolute value `<= 1000`

## Examples

**Example 1**
```
Input:  x = [0.0, 1.0, -1.0]
Output: [[0.5, 0.7310585786300049, 0.2689414213699951],
         [0.25, 0.19661193324148185, 0.19661193324148185],
         [-0.6931471805599453, -0.31326168751822286, -1.3132616875182228],
         [0.0, 0.8413447460685429, -0.15865525393145707],
         [0.5, 1.0833154705876864, -0.08331547058768629]]
Explanation: σ(0) = ½, so log σ(0) = −log 2. GELU(1) = Φ(1) ≈ 0.8413. With the
tanh approximation it would be 0.8412, which is off by more than the
tolerance.
```

**Example 2**
```
Input:  x = [3.0, -2.5]
Output: [[0.9525741268224334, 0.07585818002124356], [0.045176659730912, 0.07010371654510816],
         [-0.04858735157374206, -2.5788897342925496], [2.99595030590511, -0.015524163314440398],
         [1.011945647204184, -0.03761108590814519]]
```

**Example 3**
```
Input:  x = [-800.0, 800.0]
Output: [[0.0, 1.0], [0.0, 0.0], [-800.0, -0.0], [-0.0, 800.0], [0.0, 1.0]]
Explanation: σ(−800) underflows to 0, but log-sigmoid is still −800 (to double
precision). Computing log(σ(x)) would give −inf.
```
