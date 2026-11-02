During generation, a transformer keeps every past token's keys and values in a
**KV cache**, and for long contexts that cache dominates memory.
**Grouped-query attention** (GQA, used in Llama 2/3 and Mistral) shrinks it.
There are still `numHeads` query heads, but only `numKvHeads` key/value heads,
and each KV head is shared by a **group** of `numHeads / numKvHeads`
consecutive query heads. With `numKvHeads = numHeads` this is ordinary
multi-head attention. With `numKvHeads = 1` it is multi-query attention.

Implement causal self-attention with GQA. `X` holds $T$ tokens of width $D$.
Vectors are rows, and there are no biases. Write $H$ = `numHeads`,
$H_{kv}$ = `numKvHeads`, $d_h = D / H$ and $G = H / H_{kv}$ (the group size).
First project every token:

$$
\begin{aligned}
Q &= X W_q && T \times D \\
K &= X W_k && T \times H_{kv} d_h \\
V &= X W_v && T \times H_{kv} d_h
\end{aligned}
$$

$Q$ holds $H$ heads of width $d_h$, and $K$ and $V$ hold $H_{kv}$ heads each.
Query head $h$ ($0 \le h < H$) uses KV head $g = \lfloor h / G \rfloor$. Its
query slice $Q_h$ is columns $h d_h$ through $(h + 1) d_h - 1$ of $Q$, and
$K_g, V_g$ are columns $g d_h$ through $(g + 1) d_h - 1$ of $K$ and $V$. With
$q_i, k_j, v_j$ the rows of $Q_h, K_g, V_g$, token $i$ attends causally to
$j = 0, \dots, i$:

$$
\begin{aligned}
s_{ij} &= \frac{q_i \cdot k_j}{\sqrt{d_h}} \\
w_{ij} &= \frac{e^{s_{ij}}}{\sum_{k=0}^{i} e^{s_{ik}}} \\
o_i &= \sum_{j=0}^{i} w_{ij}\, v_j
\end{aligned}
$$

The rows $o_i$ form head $h$'s output $O_h$, and

$$
\texttt{output} = \operatorname{concat}(O_0, \dots, O_{H-1})\, W_o
$$

is $T \times D$.

So with 4 query heads and 2 KV heads, query heads 0 and 1 share KV head 0, and
query heads 2 and 3 share KV head 1. That is the layout of Llama's
`repeat_kv`, not an interleaving. The scale is $\sqrt{d_h}$, the width of one
head.

**Return `output`**, $T$ rows of $D$ numbers.

**Numerical stability matters.** Some tests have attention scores far past the
point (about 709) where `exp` overflows. Subtract each row's largest score
before exponentiating.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= T <= 32` and `1 <= D <= 32`
- `1 <= numHeads <= D` and `numHeads` divides `D`. `1 <= numKvHeads <=
  numHeads` and `numKvHeads` divides `numHeads`
- `X` is `T × D`; `Wq` and `Wo` are `D × D`; `Wk` and `Wv` are
  `D × (numKvHeads · dh)`
- Every entry is a finite number with absolute value `<= 10`

## Examples

**Example 1**
```
Input:  X  = [[1.0, 0.0, 2.0, 1.0], [0.0, 1.0, 1.0, -1.0], [2.0, -1.0, 0.0, 1.0]],
        Wq = Wo = the 4 × 4 identity,
        Wk = [[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, -1.0]],
        Wv = [[1.0, 2.0], [0.0, 1.0], [2.0, 0.0], [1.0, 1.0]],
        numHeads = 4, numKvHeads = 2
Output: [[6.0, 6.0, 3.0, 3.0],
         [3.5, 5.403985389889411, 0.14227761953270035, 2.8577223804673],
         [5.56868751663907, 1.9396098079614976, 2.333333333333333, 0.20842916991600327]]
Explanation: dh = 1 and group = 2. Query heads 0 and 1 read KV head 0 (the
first column of K and V), and heads 2 and 3 read KV head 1. Token 0 only sees
itself, so its output is V[0] = [6, 3] repeated for each pair of heads.
```

**Example 2**
```
Input:  X = [[1.0, 2.0], [3.0, -1.0]], Wq = [[1.0, 0.0], [0.0, 1.0]], Wk = [[1.0], [1.0]],
        Wv = [[2.0], [-1.0]], Wo = [[1.0, 0.0], [0.0, 1.0]], numHeads = 2, numKvHeads = 1
Output: [[0.0, 0.0], [0.3319811122429675, 5.117410050410034]]
Explanation: multi-query attention: both query heads share the single KV head,
with K = [3, 2] and V = [0, 7].
```

**Example 3**
```
Input:  X  = [[0.5, -1.0, 1.0, 2.0], [1.0, 1.0, 0.0, -1.0]],
        Wq = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 1.0, 0.0], [1.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, -1.0]],
        Wk = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 1.0, 0.0], [0.0, 1.0, -1.0, 0.0], [1.0, 0.0, 0.0, 2.0]],
        Wv = [[1.0, 0.0, 2.0, 0.0], [0.0, 1.0, 0.0, 3.0], [1.0, -1.0, 0.0, 0.0], [0.0, 2.0, 1.0, 1.0]],
        Wo = the 4 × 4 identity, numHeads = 2, numKvHeads = 2
Output: [[1.5, 2.0, 3.0, -1.0], [1.3714083423865964, 1.2284500543195789, 2.9991627987721214, -0.9987441981581813]]
Explanation: numKvHeads = numHeads, so this is plain multi-head attention with
two heads of width 2.
```
