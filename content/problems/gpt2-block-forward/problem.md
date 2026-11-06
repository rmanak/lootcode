Implement one **GPT-2 transformer block** from its weights, exactly as GPT-2
(and Hugging Face's `GPT2Block`) computes it. `x` holds $T$ token vectors of
width $d$. Vectors are rows, so every linear layer is $y = x W + b$ with $W$
stored as $(\text{in} \times \text{out})$, like GPT-2's `Conv1D`.

The attention half, where $[\, q \mid k \mid v \,]$ is the $T \times 3d$
result split into three blocks of $d$ columns:

$$
\begin{aligned}
h &= \operatorname{LayerNorm}(x;\ \texttt{ln1Gamma}, \texttt{ln1Beta}) \\
[\, q \mid k \mid v \,] &= h \cdot \texttt{attnW} + \texttt{attnB} \\
a &= \operatorname{CausalAttention}(q, k, v) \\
x &\leftarrow x + a \cdot \texttt{attnProjW} + \texttt{attnProjB}
\end{aligned}
$$

The attention uses `numHeads` heads of width $d_h = d / \texttt{numHeads}$.
Then the MLP half ($d \to 4d \to d$):

$$
\begin{aligned}
h &= \operatorname{LayerNorm}(x;\ \texttt{ln2Gamma}, \texttt{ln2Beta}) \\
z &= \operatorname{GELU}(h \cdot \texttt{fcW} + \texttt{fcB}) \\
\texttt{out} &= x + z \cdot \texttt{projW} + \texttt{projB}
\end{aligned}
$$

Both `x +` terms are residual connections. The details that matter:

- **Pre-LayerNorm**: each sub-block normalizes its *input*, and the residual
  adds the un-normalized $x$.
- **LayerNorm** normalizes each row over its $d$ values with the *biased*
  variance and $\epsilon = 10^{-5}$. With $\mu$ and $\sigma^2$ the row's mean
  and variance, it is $(x - \mu) / \sqrt{\sigma^2 + 10^{-5}} \cdot \gamma + \beta$.
- **Attention**: head $n$ uses columns $n d_h, \dots, (n + 1) d_h - 1$ of each
  of $q$, $k$ and $v$. Scores are $q_i \cdot k_j / \sqrt{d_h}$, with a softmax
  over $j \le i$ only (causal). The heads' outputs are concatenated in order.
- **GELU** is GPT-2's **tanh approximation**, not the exact $\operatorname{erf}$
  form:
  $\operatorname{GELU}(t) = \tfrac{1}{2}\, t \left(1 + \tanh\left(\sqrt{2/\pi}\, (t + 0.044715\, t^3)\right)\right)$.

`params` is an object with these twelve arrays: `ln1Gamma`, `ln1Beta`,
`ln2Gamma`, `ln2Beta`, `attnProjB` and `projB` (each $d$), `attnW`
($d \times 3d$), `attnB` ($3d$), `attnProjW` ($d \times d$), `fcW`
($d \times 4d$), `fcB` ($4d$) and `projW` ($4d \times d$).

**Return `out`**, $T$ rows of $d$ numbers.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= T <= 16` and `1 <= d <= 16`. `1 <= numHeads <= d`, and `numHeads`
  divides `d`
- `params` has exactly the twelve keys above, with the shapes above
- Every number in `x` and `params` is finite with absolute value `<= 10`

## Examples

All three examples use the same `params`, with `d = 2` (so the MLP is 8 wide):

```
params = {
  "ln1Gamma": [1.0, 1.0], "ln1Beta": [0.0, 0.0],
  "attnW": [[1.0, 0.0, 1.0, 0.0, 1.0, 2.0], [0.0, 1.0, 0.0, 1.0, -1.0, 1.0]],
  "attnB": [0.0, 0.0, 0.0, 0.0, 0.5, 0.0],
  "attnProjW": [[1.0, 0.0], [0.0, 1.0]], "attnProjB": [0.1, -0.1],
  "ln2Gamma": [1.0, 0.5], "ln2Beta": [0.0, 0.25],
  "fcW": [[1.0, -1.0, 0.5, 0.0, 2.0, 0.0, -0.5, 1.0], [0.0, 1.0, 0.5, -1.0, 0.0, 1.0, 1.0, 0.0]],
  "fcB": [0.0, 0.1, 0.0, 0.0, -0.2, 0.0, 0.0, 0.3],
  "projW": [[0.5, 0.0], [0.0, 0.5], [0.25, 0.25], [0.0, -0.5], [0.5, 0.5], [-0.25, 0.0], [0.0, 0.25], [0.5, -0.5]],
  "projB": [0.0, 0.0]
}
```

**Example 1**
```
Input:  x = [[1.0, -1.0]], params = (above), numHeads = 1
Output: [[5.560835011060206, 0.05187205901820047]]
Explanation: a single token attends only to itself, so the attention output is
its own value vector: LayerNorm([1, −1]) ≈ [1, −1], v = [1·1 + (−1)·(−1) + 0.5,
1·2 + (−1)·1] = [2.5, 1].
```

**Example 2**
```
Input:  x = [[1.0, -1.0], [0.5, 2.0], [-1.0, 0.0]], params = (above), numHeads = 1
Output: [[5.560835011060206, 0.05187205901820058], [-1.015085581507568, 2.3267920085365397],
         [-2.6234843660426526, 0.27258557042915976]]
Explanation: token 0 matches Example 1, up to the last bit of rounding,
because of the causal mask. The later tokens also attend to earlier ones.
```

**Example 3**
```
Input:  the same x and params as Example 2, numHeads = 2
Output: [[5.560835011060206, 0.05187205901820058], [-0.7615006055953293, 2.453583089563195],
         [-2.4847834174239862, 0.34193417377185065]]
Explanation: two heads of width 1. Head 0 uses column 0 of q, k and v, and
head 1 uses column 1, each scaled by 1/√1.
```
