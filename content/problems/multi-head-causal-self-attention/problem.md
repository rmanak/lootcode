# Multi-Head Causal Self-Attention

A decoder-only transformer (GPT-style) mixes information between the tokens of a
sequence with **multi-head causal self-attention**. Every token is projected into
a query, a key and a value; the projections are cut into `numHeads` smaller
**heads** that attend independently; and the heads' outputs are glued back
together and projected once more. "Causal" means a token may only attend to
itself and the tokens **before** it, never to later ones.

`X` holds $T$ tokens (rows) of width $D$. The four weight matrices are
$D \times D$, vectors are rows, and there are no bias terms. Let $H$ =
`numHeads` and $d_h = D / H$. First project every token, giving three
$T \times D$ matrices:

$$
Q = X W_q, \quad K = X W_k, \quad V = X W_v
$$

Head $h$ ($h = 0, 1, \dots, H - 1$) uses columns $h d_h$ through
$(h + 1) d_h - 1$ of $Q$, $K$ and $V$: call those $T \times d_h$ slices
$Q_h, K_h, V_h$, and their rows $q_i, k_j, v_j$. Token $i$ attends to the
tokens $j \le i$ only, with a softmax over $j = 0, \dots, i$:

$$
\begin{aligned}
s_{ij} &= \frac{q_i \cdot k_j}{\sqrt{d_h}} \\
w_{ij} &= \frac{e^{s_{ij}}}{\sum_{k=0}^{i} e^{s_{ik}}} \\
o_i &= \sum_{j=0}^{i} w_{ij}\, v_j
\end{aligned}
$$

The rows $o_i$ form head $h$'s output $O_h$ ($T \times d_h$). The heads are
then placed side by side ($T \times D$) and projected:

$$
\texttt{output} = \operatorname{concat}(O_0, O_1, \dots, O_{H-1})\, W_o
$$

**Return `output`**, $T$ rows of $D$ numbers. Note the scale is
$\sqrt{d_h}$, the width of one head, not $\sqrt{D}$.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

**Numerical stability matters.** Some tests have scores in the tens of
thousands, far past the point (about 709) where `exp` overflows a float.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= T <= 32` and `1 <= D <= 32`
- `X` is `T × D`; `Wq`, `Wk`, `Wv` and `Wo` are each `D × D`
- Every entry of `X` and of the weights is a finite number with absolute value
  `<= 10`
- `1 <= numHeads <= D`, and `numHeads` divides `D` exactly

## Examples

**Example 1**
```
Input:  X  = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
        Wq = [[1.0, 0.0], [0.0, 1.0]],  Wk = [[1.0, 0.0], [0.0, 1.0]],
        Wv = [[1.0, 2.0], [3.0, 4.0]],  Wo = [[1.0, 0.0], [0.0, 1.0]],
        numHeads = 1
Output: [[1.0, 2.0],
         [2.3395230986533138, 3.3395230986533138],
         [3.0069796869691077, 4.510469530453662]]
Explanation: token 0 can only attend to itself, so its output is its own value
X₀ · Wv = [1, 2]. Token 1 attends to tokens 0 and 1 with scores 0 and 1/√2.
```

**Example 2**
```
Input:  X  = [[1.0, 0.0, 2.0, 0.0], [0.0, 1.0, 0.0, -1.0], [2.0, 1.0, 1.0, 1.0]],
        Wq = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 1.0, 0.0], [1.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, -1.0]],
        Wk = [[0.0, 1.0, 1.0, 0.0], [1.0, 0.0, 0.0, 1.0], [0.0, 1.0, -1.0, 0.0], [1.0, 0.0, 0.0, 2.0]],
        Wv = [[1.0, 0.0, 2.0, 0.0], [0.0, 1.0, 0.0, 3.0], [1.0, -1.0, 0.0, 0.0], [0.0, 2.0, 1.0, 1.0]],
        Wo = [[0.5, 0.0, 0.0, 1.0], [0.0, 0.5, 1.0, 0.0], [1.0, 0.0, 0.5, 0.0], [0.0, -1.0, 0.0, 0.5]],
        numHeads = 2
Output: [[3.5, -1.0, -1.0, 3.0],
         [2.348721945782215, -1.606956000614101, -1.3883158745448443, 3.009113046277832],
         [6.394478934504327, -2.9727505166670736, 4.390128938695871, 4.971448910065927]]
Explanation: head 0 uses columns 0–1 of Q, K and V; head 1 uses columns 2–3.
```

**Example 3**
```
Input:  X  = [[2.0, 0.0, 1.0, -1.0], [0.0, 3.0, -1.0, 1.0]],
        Wq = Wk = Wo = the 4 × 4 identity,
        Wv = [[1.0, 0.0, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0], [0.0, 0.0, 3.0, 0.0], [0.0, 0.0, 0.0, 4.0]],
        numHeads = 4
Output: [[2.0, 0.0, 3.0, -4.0],
         [1.0, 5.999259632544082, -2.2847824678672946, 3.046376623823059]]
Explanation: four heads of width 1. For token 1, head 0 has query 0, so both
scores are 0 and it averages its two values (2 and 0) to 1. Head 1 scores
token 1 at 9 and token 0 at 0, so it almost copies token 1's value, 6.
```

(In the tests every matrix is written out in full; Example 3 abbreviates the
identity matrices.)
