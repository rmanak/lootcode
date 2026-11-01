# DPO Loss: Direct Preference Optimization

**DPO** aligns a language model with human preferences without training a
reward model or running RL. For each prompt there is a *chosen* (preferred)
response and a *rejected* one. DPO pushes the policy to raise the chosen
response's likelihood, relative to a frozen **reference** model, more than the
rejected one's. Implement the loss as Hugging Face TRL's `DPOTrainer`
computes it, from sequence log-probabilities that are already summed over each
response's tokens.

For pair $i$, with $\pi_\theta$ the policy, $\pi_{\text{ref}}$ the reference,
$y_w$ the chosen response and $y_l$ the rejected one, the four inputs are
sequence log-probabilities: `policyChosen[i]` $= \log \pi_\theta(y_w)$,
`policyRejected[i]` $= \log \pi_\theta(y_l)$, `refChosen[i]`
$= \log \pi_{\text{ref}}(y_w)$ and `refRejected[i]`
$= \log \pi_{\text{ref}}(y_l)$. The quantity everything is built on is

$$
\begin{aligned}
h_i &= \log \frac{\pi_\theta(y_w)}{\pi_{\text{ref}}(y_w)} - \log \frac{\pi_\theta(y_l)}{\pi_{\text{ref}}(y_l)} \\[1ex]
    &= (\texttt{policyChosen}_i - \texttt{policyRejected}_i) \\
    &\quad - (\texttt{refChosen}_i - \texttt{refRejected}_i)
\end{aligned}
$$

**`lossType = "sigmoid"`** (the DPO paper), with $\beta$ = `beta`, optional
label smoothing $\varepsilon$ = `labelSmoothing` (conservative DPO, for noisy
preference labels), and $z_i = \beta h_i$:

$$
\ell_i = -(1 - \varepsilon) \log \sigma(z_i) \;-\; \varepsilon \log \sigma(-z_i)
$$

**`lossType = "ipo"`** (Identity Preference Optimization), where
`labelSmoothing` is always `0`:

$$
\ell_i = \left( h_i - \frac{1}{2\beta} \right)^{2}
$$

Also report DPO's **implicit rewards**, the quantities TRL logs during
training:

$$
\begin{aligned}
\texttt{chosenRewards}_i &= \beta \log \frac{\pi_\theta(y_w)}{\pi_{\text{ref}}(y_w)} \\[1ex]
\texttt{rejectedRewards}_i &= \beta \log \frac{\pi_\theta(y_l)}{\pi_{\text{ref}}(y_l)}
\end{aligned}
$$

and `rewardAccuracy`, the fraction of pairs whose chosen reward is
**strictly** greater than their rejected reward.

**Return `[loss, chosenRewards, rejectedRewards, rewardAccuracy, gradChosen,
gradRejected]`**, where `loss` $= \frac{1}{B} \sum_i \ell_i$ is the **mean**
over the batch, `gradChosen[i]` is
$\partial\, \texttt{loss} / \partial\, \texttt{policyChosen}_i$, and
`gradRejected[i]` is
$\partial\, \texttt{loss} / \partial\, \texttt{policyRejected}_i$.

**Stability.** $z$ can reach about $\pm 1500$. $\log \sigma(z)$ must be
computed without forming $\sigma(z)$, which underflows to 0. Use
$\log \sigma(z) = -\log\left(1 + e^{-z}\right)$, written so it never
exponentiates a large positive number.

You may use **numpy** and the Python standard library. Numpy arrays and numpy
scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. Two rewards in a pair are never within
a relative `1e-9` of each other unless they are exactly equal, and then both
subtractions are exact in floating point.

## Constraints

- The four log-prob lists have the same length `B`, with `1 <= B <= 1000`
- Every log-prob is a finite number in `[−10⁴, 0]`
- `0 < β <= 10`
- `lossType` is `"sigmoid"` or `"ipo"`. `0 <= labelSmoothing < 0.5`, and it
  is `0` whenever `lossType` is `"ipo"`

## Examples

**Example 1**
```
Input:  policyChosen = [-10.0, -12.0], policyRejected = [-14.0, -11.0], refChosen = [-11.0, -12.0],
        refRejected = [-13.0, -12.0], beta = 0.1, labelSmoothing = 0.0, lossType = "sigmoid"
Output: [0.6712677647275813, [0.1, 0.0], [-0.1, 0.1], 0.5,
         [-0.022508300134376106, -0.026248959373947], [0.022508300134376106, 0.026248959373947]]
Explanation: pair 0 has h = (−10 + 14) − (−11 + 13) = 2. The policy already
prefers the chosen response more than the reference does. Pair 1 has h = −1.
The gradient on a chosen log-prob is negative: raising it lowers the loss.
```

**Example 2**
```
Input:  policyChosen = [-10.0, -12.0, -5.0], policyRejected = [-14.0, -11.0, -6.0],
        refChosen = [-11.0, -12.0, -5.5], refRejected = [-13.0, -12.0, -6.5],
        beta = 0.5, labelSmoothing = 0.1, lossType = "sigmoid"
Output: [0.6768286174194249, [0.5, 0.0, 0.25], [-0.5, 0.5, 0.25], 0.3333333333333333,
         [-0.028156903561665853, -0.0870765552003091, -0.06666666666666667],
         [0.028156903561665853, 0.0870765552003091, 0.06666666666666667]]
Explanation: the third pair's rewards tie at 0.25, so that pair does not count
as correct.
```

**Example 3**
```
Input:  the same log-probs as Example 1, beta = 0.1, labelSmoothing = 0.0, lossType = "ipo"
Output: [22.5, [0.1, 0.0], [-0.1, 0.1], 0.5, [-3.0, -6.0], [3.0, 6.0]]
Explanation: IPO regresses h towards 1 / (2β) = 5. The losses are
(2 − 5)² = 9 and (−1 − 5)² = 36, with mean 22.5.
```
