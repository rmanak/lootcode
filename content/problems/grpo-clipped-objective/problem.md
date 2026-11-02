**GRPO** (Group Relative Policy Optimization, from DeepSeekMath and used to
train DeepSeek-R1) is PPO without a value network. For each prompt the model
samples a **group** of $G$ completions, and each completion's advantage is
simply how much better its reward is than the rest of its group. Implement
the GRPO loss.

**Inputs.** `rewards` is $B \times G$: $B$ prompts with $G$ scored completions
each. The token-level log-probabilities come as flat lists of $B G$
completions in group-major order, so completion `k` belongs to prompt
`k // G` and is its item `k % G`. Completions have different lengths. For
each token there are three log-probs: `newLogps` ($\log \pi_\theta$) from the
policy being trained, `oldLogps` ($\log \pi_\text{old}$) from the policy that
sampled the completion, and `refLogps` ($\log \pi_\text{ref}$) from the frozen
reference model.

**1. Advantages**, one per completion. For a group with rewards
$r_1, \dots, r_G$, use the mean $\bar r$ and the **sample** standard deviation
$\sigma$ (divide by $G - 1$, as `torch.std` does):

$$
\begin{aligned}
\bar r &= \frac{1}{G} \sum_{g=1}^{G} r_g \\
\sigma &= \sqrt{\frac{1}{G - 1} \sum_{g=1}^{G} (r_g - \bar r)^2} \\
A_g &= \frac{r_g - \bar r}{\sigma + 10^{-4}}
\end{aligned}
$$

The $10^{-4}$ keeps a group with identical rewards from dividing by zero.

**2. Per-token loss**, with $\varepsilon$ = `clipEps` and $\beta$ = `beta`.
Every token of a completion uses that completion's $A$. For each token, the
probability ratio $\rho$, the clipped surrogate $s$, the KL penalty $\mathrm{kl}$ (the
"k3" estimator, always $\ge 0$) and the token loss $\ell$ are

$$
\begin{aligned}
\rho &= e^{\log \pi_\theta - \log \pi_\text{old}} \\
s &= \min\big(\rho A,\; \operatorname{clip}(\rho, 1 - \varepsilon, 1 + \varepsilon)\, A\big) \\
\Delta &= \log \pi_\text{ref} - \log \pi_\theta \\
\mathrm{kl} &= e^{\Delta} - \Delta - 1 \\
\ell &= -(s - \beta\, \mathrm{kl})
\end{aligned}
$$

**3. Aggregation.** With `aggregation = "sequence"`, average the token losses
within each completion, then average over the $B G$ completions. This is the
original GRPO, and it gives every completion equal weight. With
`aggregation = "token"`, average over all tokens of all completions, so every
token has equal weight. `meanKl` is the mean of the per-token $\mathrm{kl}$ values,
aggregated the same way.

**4. Clip fraction.** A token is *clipped* when the clip actually bites:
$\rho > 1 + \varepsilon$ with $A > 0$, or $\rho < 1 - \varepsilon$ with
$A < 0$. `clipFraction` is the number of clipped tokens divided by the total
number of tokens, whatever the aggregation.

**Return `[advantages, loss, clipFraction, meanKl]`**, where `advantages` is
$B \times G$.

You may use the Python standard library and **numpy**. Numpy arrays and numpy
scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. Each advantage is either exactly 0
(the reward equals its group's mean) or at least `1e-9` in size. No token with
a non-zero advantage has a ratio within a relative `1e-9` of
$1 \pm \varepsilon$.

## Constraints

- `1 <= B <= 8` and `2 <= G <= 16`, and every reward has absolute value
  `<= 100`
- `newLogps`, `oldLogps` and `refLogps` each hold `B·G` completions. The
  three agree on each completion's length, which is `1` to `64` tokens
- Every log-prob is a finite number in `[−50, 0]`
- `0 < clipEps <= 0.5` and `0 <= beta <= 1`
- `aggregation` is `"sequence"` or `"token"`

## Examples

**Example 1**
```
Input:  rewards = [[1.0, 0.0]], newLogps = [[-1.0, -2.0], [-1.5]], oldLogps = [[-1.0, -2.0], [-1.5]],
        refLogps = [[-1.0, -2.0], [-1.5]], clipEps = 0.2, beta = 0.0, aggregation = "sequence"
Output: [[[0.7070067953266834, -0.7070067953266834]], 0.0, 0.0, 0.0]
Explanation: the sample std of [1, 0] is √0.5, so A = ±0.5 / (0.70711 + 0.0001).
Every ratio is 1 and the policy matches the reference, so the surrogates are
±A. They cancel in the average, and nothing is clipped.
```

**Example 2**
```
Input:  rewards = [[1.0, 0.0, 0.0]],
        newLogps = [[-0.594535], [-0.594535, -2.0], [-3.693147]],
        oldLogps = [[-1.0], [-1.0, -2.0], [-3.0]],
        refLogps = [[-1.0], [-1.2, -2.0], [-3.0]], clipEps = 0.2, beta = 0.1, aggregation = "token"
Output: [[[1.1545005730142688, -0.5772502865071343, -0.5772502865071343]], 0.14313803952901977, 0.5,
         0.13256748466964152]
Explanation: the ratios are about 1.5, 1.5, 1 and 0.5. Completion 0 (A > 0,
ratio 1.5) and completion 2 (A < 0, ratio 0.5) are clipped. Completion 1's
first token also has ratio 1.5, but its A is negative, so the min selects the
unclipped 1.5·A and that token does not count as clipped. 2 of 4 tokens are
clipped.
```

**Example 3**
```
Input:  the same as Example 2, with aggregation = "sequence"
Output: [[[1.1545005730142688, -0.5772502865071343, -0.5772502865071343]], -0.052191643755573947, 0.5,
         0.1515423860495814]
Explanation: now completion 1's two tokens are averaged first, so each
completion carries the same weight.
```
