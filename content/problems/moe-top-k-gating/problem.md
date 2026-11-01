# Mixture of Experts: Top-k Routing with Capacity

A **mixture-of-experts** (MoE) layer, as in Mixtral, Switch Transformer and
DeepSeek-V3, holds $E$ expert networks but runs only $k$ of them per token. A
small **router** picks the experts. Implement the routing, the capacity limit,
the combination of expert outputs, and the load-balancing loss.

`X` holds $T$ tokens $x_t$ of width $d$. The router is $W_g$ = `Wg`
($d \times E$), and expert $e$ is the linear map $x \mapsto x\, M_e$, where
$M_e$ = `experts[e]` is $d \times d$.

**1. Route.** The router logits are $Z = X W_g$ ($T \times E$). Each token
picks its $k$ experts with the largest logits, listed from highest to lowest.
**Equal logits go to the lower expert index.** Its $k$ gates are a **softmax
over just those $k$ logits**, Mixtral style, so they sum to 1: with
$e_1, \dots, e_k$ the token's chosen experts,

$$
g_{t,r} = \frac{\exp(Z_{t, e_r})}{\sum_{r'=1}^{k} \exp(Z_{t, e_{r'}})}
$$

**2. Capacity.** Each expert can accept at most `capacity` assignments. Go
through the tokens in order $t = 0, 1, \dots$, and through each token's
choices in rank order. An assignment to an expert that already has `capacity`
assignments is **dropped**. A dropped assignment contributes nothing, and the
token's other gates are **not** renormalized.

**3. Combine.** Each token's output sums over its kept assignments, and is all
zeros if every one was dropped:

$$
y_t = \sum_{r \,\text{kept}} g_{t,r}\; x_t M_{e_r}
$$

**4. Load-balancing loss** (Switch Transformer). Let $P_e$ be the mean over
tokens of the router's softmax over **all $E$** logits, and $f_e$ the
fraction of tokens whose **top-1** expert is $e$. Both are computed before
capacity. Then

$$
\texttt{auxLoss} = E \sum_{e=0}^{E-1} f_e\, P_e
$$

This is 1 for a perfectly balanced router, and larger when routing
concentrates on a few experts.

**Return `[expertIndices, gates, output, tokensPerExpert, auxLoss]`**:
`expertIndices` and `gates` are $T \times k$ in rank order, `output` is
$T \times d$, and `tokensPerExpert[e]` is the number of assignments expert $e$
kept.

**Stability.** Logits can reach the thousands. Shift by the maximum before
exponentiating.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Integers must match exactly. Floats are accepted when every number is within a
relative `1e-6` (or an absolute `1e-9`) of the expected value. Among each
token's top $k + 1$ logits, two are within a relative `1e-9` only if they are
exactly equal, and exact ties appear only when `X` and `Wg` are
integer-valued, so every implementation computes them exactly.

## Constraints

- `1 <= T <= 64`, `1 <= d <= 16` and `1 <= E <= 16`
- `X` is `T × d`, `Wg` is `d × E`, and `experts` is `E × d × d`
- Every entry is finite with absolute value `<= 10`
- `1 <= k <= E` and `1 <= capacity <= T`

## Examples

**Example 1**
```
Input:  X = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], Wg = [[2.0, 0.0, 1.0], [0.0, 2.0, 1.0]],
        experts = [[[1.0, 0.0], [0.0, 1.0]], [[2.0, 0.0], [0.0, 2.0]], [[0.0, 1.0], [1.0, 0.0]]],
        k = 2, capacity = 3
Output: [[[0, 2], [1, 2], [0, 1]],
         [[0.7310585786300049, 0.2689414213699951], [0.7310585786300049, 0.2689414213699951], [0.5, 0.5]],
         [[0.7310585786300049, 0.2689414213699951], [0.2689414213699951, 1.4621171572600098], [1.5, 1.5]],
         [2, 2, 2], 1.0886048622785356]
Explanation: token 2's logits are [2, 2, 2], a three-way tie, so it takes
experts 0 and 1 (the lowest indices) with equal gates.
```

**Example 2**
```
Input:  X = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], Wg = [[2.0, 1.0, 0.0], [0.0, 2.0, 1.0]],
        experts = the same three experts as Example 1, k = 2, capacity = 1
Output: [[[0, 1], [1, 2], [1, 0]],
         [[0.7310585786300049, 0.2689414213699951], [0.7310585786300049, 0.2689414213699951],
          [0.7310585786300049, 0.2689414213699951]],
         [[1.2689414213699952, 0.0], [0.2689414213699951, 0.0], [0.0, 0.0]], [1, 1, 1], 1.3834735884029608]
Explanation: token 0 comes first and fills experts 0 and 1, so token 1 loses
its top choice (expert 1) and keeps only expert 2, with gate 0.269. That gate
is not renormalized. Token 2's choices are all full, so its output is zero.
```

**Example 3**
```
Input:  X = [[0.0, 0.0], [1.0, -1.0], [1.0, 2.0]], Wg = [[1.0, 1.0, 0.0, 0.0], [0.0, 1.0, 1.0, 0.0]],
        experts = [[[1.0, 0.0], [0.0, 1.0]], [[0.5, 0.0], [0.0, 0.5]], [[1.0, 1.0], [0.0, 1.0]],
                   [[-1.0, 0.0], [0.0, 1.0]]], k = 1, capacity = 2
Output: [[[0], [0], [1]], [[1.0], [1.0], [1.0]], [[0.0, 0.0], [1.0, -1.0], [0.5, 1.0]], [2, 1, 0, 0],
         1.25942583172914]
Explanation: token 0 is all zeros, so every logit is 0 and expert 0 wins the
tie. With k = 1 each gate is 1.
```
