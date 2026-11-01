# Adam Optimizer

**Adam** is the default optimizer for training neural networks. For every
parameter it keeps a running average of the gradient (the **first moment**,
like momentum) and of the squared gradient (the **second moment**), and it
scales each step by their ratio. Every parameter thus gets its own step size.

Implement the `Adam` class:

- `Adam(params, lr, beta1, beta2, eps)`: an optimizer for the parameter vector
  `params` (a list of `d` numbers), with learning rate `lr`, decay rates
  `beta1` and `beta2`, and the small constant `eps`. Both moment vectors start
  at all zeros, and the step counter `t` starts at `0`.
- `step(grad)`: apply one update with the gradient `grad` (`d` numbers) and
  return the updated parameters (`d` numbers).

One step does this, elementwise over the `d` entries, where $\theta$ is
`params`, $g$ is `grad`, $\eta$ is `lr`, $\beta_1, \beta_2$ are `beta1`,
`beta2`, and $\epsilon$ is `eps`:

$$
\begin{aligned}
t &\leftarrow t + 1 \\
m &\leftarrow \beta_1\, m + (1 - \beta_1)\, g \\
v &\leftarrow \beta_2\, v + (1 - \beta_2)\, g^2 \\
\hat m &= \frac{m}{1 - \beta_1^{\,t}}, \qquad \hat v = \frac{v}{1 - \beta_2^{\,t}} \\
\theta &\leftarrow \theta - \eta\, \frac{\hat m}{\sqrt{\hat v} + \epsilon}
\end{aligned}
$$

The hats are the **bias correction**: $m$ and $v$ start at $0$, so without it
the first steps' averages are too small. Note that $\epsilon$ is added **after**
the square root.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value of `step`.

Every number `step` returns is accepted when it is within a relative `1e-6` (or
an absolute `1e-9`) of the expected value.

## Constraints

- `1 <= d <= 50`, and every entry of `params` is a finite number with absolute
  value `<= 100`
- `0 < lr <= 1`, `0 <= beta1 < 1`, `0 <= beta2 < 1`, `1e-12 <= eps <= 1`
- Every `grad` has exactly `d` entries, each a finite number with absolute value
  `<= 1000`
- At most `200` calls to `step`

## Examples

**Example 1**

```
Input
["Adam", "step", "step", "step"]
[[[1.0, -1.0], 0.1, 0.9, 0.999, 1e-08], [[2.0, -0.5]], [[2.0, -0.5]], [[-1.0, 0.0]]]

Output
[null, [0.9000000005, -0.900000002], [0.8000000010000007, -0.8000000040000006],
 [0.7484346607192304, -0.7226997160627585]]
```

Explanation: on the first step bias correction makes `m̂ = grad` and
`v̂ = grad²`, so every parameter moves by almost exactly `lr` against the sign
of its gradient, whatever the gradient's size. A repeated gradient repeats
that. The third gradient flips sign, but momentum still carries both
parameters the same way, just less far.

**Example 2**

```
Input
["Adam", "step", "step"]
[[[0.0, 5.0, -3.0], 0.5, 0.5, 0.75, 0.1], [[0.0, 1.0, -4.0]], [[0.0, 3.0, 2.0]]]

Output
[null, [0.0, 4.545454545454546, -2.5121951219512195], [0.0, 4.071274472276157, -2.5121951219512195]]
```

Explanation: a zero gradient never moves its parameter. A large `eps` (`0.1`)
visibly shortens the first step: `0.5 · 1 / (1 + 0.1) ≈ 0.4545`. For the third
parameter, the gradients `−4` and then `2` cancel in the first moment
(`0.5 · (−2) + 0.5 · 2 = 0`), so the second step leaves it where it was.

**Example 3**

```
Input
["Adam", "step", "step", "step", "step"]
[[[10.0], 1.0, 0.8, 0.9, 0.01], [[4.0]], [[2.0]], [[1.0]], [[0.5]]]

Output
[null, [9.002493765586035], [8.077145121040353], [7.2496232159791365], [6.527359107136762]]
```

Explanation: the gradient halves every step, but each step stays close to
`lr`, because Adam divides the gradient by its own running magnitude.
