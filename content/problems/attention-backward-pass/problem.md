Implement single-head **scaled dot-product attention**, forward and backward,
without an autograd library. `Q` is $n \times d$ (queries), `K` is
$m \times d$ (keys) and `V` is $m \times d_v$ (values). The forward pass is

$$
\begin{aligned}
S &= \frac{Q K^\top}{\sqrt{d}} + M \\[1ex]
P_{ij} &= \frac{e^{S_{ij}}}{\sum_{k} e^{S_{ik}}} \\[1ex]
O &= P V
\end{aligned}
$$

where the mask $M$ is all zeros unless `causal` is true. With `causal`, the
tests have $n = m$ and query $i$ may only attend to keys $j \le i$:
$M_{ij} = -\infty$ for $j > i$, so $P_{ij} = 0$ there.

**Backward.** `dO` ($n \times d_v$) is the upstream gradient
$\partial L / \partial O$. Compute $\texttt{dQ} = \partial L / \partial Q$,
$\texttt{dK} = \partial L / \partial K$ and $\texttt{dV} = \partial L / \partial V$
by pushing `dO` back through each step: the product $O = PV$, the row-wise
softmax, and the scaled product $QK^\top$. For the softmax, recall that each
row's Jacobian is $\operatorname{diag}(p) - p\,p^\top$, so it can be applied to a
row of upstream gradients without forming the matrix.

**Return `[O, dQ, dK, dV]`**, with the shapes of `dO`, `Q`, `K` and `V`.

Scores in the tests reach the hundreds, so compute the softmax stably
(subtract each row's maximum before exponentiating).

You may use **numpy** and the Python standard library. Numpy arrays are fine as
return values.

## Constraints

- `1 <= n, m <= 64` and `1 <= d, d_v <= 32`
- Every entry of `Q`, `K`, `V` and `dO` is finite with absolute value `<= 30`
- When `causal` is `true`, `n == m`

## Examples

**Example 1**
```
Input:  Q = [[1.0, 0.0]], K = [[1.0, 0.0], [0.0, 1.0]], V = [[1.0], [3.0]], dO = [[1.0]], causal = false
Output: [[[1.6604769013466862]], [[-0.3127971930902208, 0.3127971930902208]],
         [[-0.3127971930902208, 0.0], [0.3127971930902208, 0.0]], [[0.6697615493266569], [0.3302384506733431]]]
Explanation: the scores are 1/√2 ≈ 0.707 and 0, so P ≈ [0.670, 0.330] and
O ≈ 0.670·1 + 0.330·3 ≈ 1.660. dV = Pᵀ·dO is just P. dP = dO·Vᵀ = [1, 3], so
the softmax backward gives dS = P ⊙ (dP − O) ≈ [−0.442, 0.442]; dQ and dK
are that times K and Q, divided by √2.
```

**Example 2**
```
Input:  Q = [[0.0, 0.0], [2.0, 0.0]], K = [[1.0, 1.0], [2.0, -1.0]], V = [[1.0, 0.0], [0.0, 1.0]],
        dO = [[1.0, 0.0], [0.0, 1.0]], causal = true
Output: [[[1.0, 0.0], [0.19557031749304313, 0.8044296825069569]],
         [[0.0, 0.0], [0.11124385495548571, -0.22248770991097155]],
         [[-0.22248770991097158, 0.0], [0.2224877099109715, 0.0]],
         [[1.0, 0.19557031749304313], [0.0, 0.8044296825069569]]]
Explanation: query 0 sees only key 0, so its softmax is [1] and it passes no
gradient to Q or K (a one-entry softmax is constant). Query 1 sees both keys
with scores √2 and 2√2.
```

**Example 3**
```
Input:  Q = [[1.0, 2.0], [0.0, -1.0], [3.0, 1.0]], K = [[0.5, 0.0], [-1.0, 1.0], [2.0, 0.0]],
        V = [[1.0, 2.0], [0.0, -1.0], [2.0, 0.0]], dO = [[1.0, 0.0], [0.5, 0.5], [0.0, -1.0]], causal = false
Output: [[[1.275611618824052, 0.1084032450707535], [1.2033362780393577, 0.6044483707191437],
          [1.9535976080107853, 0.07608947413362548]],
         [[0.7804329708919635, -0.24180167376400985], [0.33538700316426306, -0.19633240375352864],
          [0.07341431351094893, 0.002543769832145171]],
         [[-0.19877654574805814, -0.29647448686905004], [-0.23417036426757434, -0.28472717394234587],
          [0.43294691001563246, 0.581201660811396]],
         [[0.388795020603384, 0.1608397782885998], [0.36696261077644265, 0.09554484535125322],
          [0.7442423686201735, -0.756384623639853]]]
```
