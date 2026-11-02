Most large models train with the same learning-rate shape. The rate climbs
linearly from `0` during a short **warmup**, then follows half a cosine wave
down to a floor, and then stays there. Given a list of step numbers, return
the learning rate at each one.

With $b$ = `baseLr`, $m$ = `minLr`, $w$ = `warmupSteps` and $T$ =
`totalSteps`, the rate at step $t$ is a linear warmup (exactly $0$ at step
$0$), then the cosine phase, then the floor:

$$
\text{lr}(t) =
\begin{cases}
  b \cdot \dfrac{t}{w} & t < w \\[2ex]
  m + \dfrac{b - m}{2} \left( 1 + \cos\!\left( \pi \cdot \dfrac{t - w}{T - w} \right) \right) & w \le t < T \\[2ex]
  m & t \ge T
\end{cases}
$$

The cosine phase starts at exactly $b$ at step $w$ and reaches $m$ at step
$T$. When $w = 0$ there is no warmup, and step 0 already has the rate $b$.

The steps are not necessarily sorted, and they can repeat. **Return one learning rate per
entry of `steps`**, in the same order.

You may use the Python standard library and **numpy**. A numpy array is fine
as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= len(steps) <= 10⁴`, and every step is an integer in `[0, 2·10⁶]`
- `0 <= minLr <= baseLr <= 10`
- `0 <= warmupSteps < totalSteps <= 10⁶`

## Examples

**Example 1**
```
Input:  steps = [0, 1, 2, 3, 4, 6, 8, 10, 12], baseLr = 1.0, minLr = 0.0, warmupSteps = 2, totalSteps = 10
Output: [0.0, 0.5, 1.0, 0.9619397662556434, 0.8535533905932737, 0.5, 0.14644660940672627, 0.0, 0.0]
Explanation: steps 0 and 1 warm up to 0.5. The cosine runs from step 2 to
step 10, an 8-step span, so step 6 is halfway down and gets 0.5. From step 10
onwards the rate stays at minLr = 0.
```

**Example 2**
```
Input:  steps = [0, 50, 100, 300, 550, 1000, 1500], baseLr = 0.001, minLr = 0.0001,
        warmupSteps = 100, totalSteps = 1000
Output: [0.0, 0.0005, 0.001, 0.00089471999940354, 0.00055, 0.0001, 0.0001]
Explanation: step 550 is halfway through the cosine phase (100 to 1000), so
the rate is midway between 0.001 and 0.0001.
```

**Example 3**
```
Input:  steps = [5, 0, 5, 20, 19], baseLr = 0.5, minLr = 0.1, warmupSteps = 0, totalSteps = 20
Output: [0.4414213562373095, 0.5, 0.4414213562373095, 0.1, 0.10246233188097248]
Explanation: with no warmup, step 0 is already at baseLr. The steps are not sorted, and
step 5 appears twice.
```
