# Classifier-Free Guidance with Rescale

Text-to-image diffusion models follow the prompt more closely thanks to
**classifier-free guidance** (CFG). At each denoising step the model predicts
the noise twice, once with the prompt (*conditional*, $c$) and once without it
(*unconditional*, $u$). The final prediction $g$ extrapolates from the
unconditional prediction towards the conditional one, with $w$ =
`guidanceScale`:

$$
g = u + w\, (c - u)
$$

A scale of 1 gives the conditional prediction, and larger scales push harder
towards the prompt. Large scales also over-saturate images, so diffusers
offers **guidance rescale** (Lin et al., 2023). It rescales each sample's
guided prediction to the standard deviation of its conditional prediction,
giving $\tilde g$, then blends, with $\phi$ = `guidanceRescale`:

$$
\begin{aligned}
\tilde g &= g \cdot \frac{\operatorname{std}(c)}{\operatorname{std}(g)} \\[1ex]
\text{result} &= \phi\, \tilde g + (1 - \phi)\, g
\end{aligned}
$$

Each $\operatorname{std}$ is taken per sample, over all $N$ values. With
$\phi = 0$ the result is just $g$.

**Input layout.** For speed, both predictions come from one forward pass over
a doubled batch, so `noisePred` has $2B$ rows of $N$ values (one flattened
latent per row). The **first $B$ rows are unconditional** and the **last $B$
are conditional**, the order diffusers gets from `noise_pred.chunk(2)`.
Unconditional row $i$ pairs with conditional row $B + i$.

$\operatorname{std}$ is the standard deviation over a row's $N$ values.
Whether it divides by $N$ or $N - 1$ makes no difference, because only the
ratio of two $\operatorname{std}$s is used.

**Return the $B \times N$ result**.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `noisePred` has `2B` rows with `1 <= B <= 16`, each of `N` values with
  `2 <= N <= 256`
- Every value is finite with absolute value `<= 100`
- `0 <= guidanceScale <= 20` and `0 <= guidanceRescale <= 1`
- When `guidanceRescale > 0`, every conditional row and every `guided` row has
  a standard deviation of at least `1e-3`

## Examples

**Example 1**
```
Input:  noisePred = [[0.0, 1.0, 2.0], [1.0, 1.0, 4.0]], guidanceScale = 3.0, guidanceRescale = 0.0
Output: [[3.0, 1.0, 8.0]]
Explanation: B = 1, so the unconditional row is [0, 1, 2] and the conditional
row is [1, 1, 4]. guided = [0, 1, 2] + 3 · [1, 0, 2] = [3, 1, 8].
```

**Example 2**
```
Input:  noisePred = [[0.0, 1.0, 2.0], [1.0, 1.0, 4.0]], guidanceScale = 3.0, guidanceRescale = 0.7
Output: [[1.908807368972049, 0.636269122990683, 5.090152983925464]]
Explanation: guided = [3, 1, 8]. Its squared deviations sum to 26, and those
of cond = [1, 1, 4] sum to 6, so std(cond) / std(guided) = √(6/26) ≈ 0.4804.
The result is guided · (0.7 · 0.4804 + 0.3) ≈ 0.6363 · guided.
```

**Example 3**
```
Input:  noisePred = [[1.0, -1.0], [0.0, 2.0], [2.0, -2.0], [2.0, 1.0]], guidanceScale = 2.0,
        guidanceRescale = 1.0
Output: [[2.0, -2.0], [1.0, 0.0]]
Explanation: B = 2. Sample 0 pairs [1, −1] with [2, −2]: guided = [3, −3],
rescaled by 2/3 to [2, −2]. Sample 1 pairs [0, 2] with [2, 1]: guided =
[4, 0], rescaled by 1/4. Each sample uses its own standard deviations.
```
