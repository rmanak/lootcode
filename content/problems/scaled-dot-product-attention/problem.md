# Scaled Dot-Product Attention

**Attention** is the core operation of a transformer. Each **query** vector
scores every **key** vector by a dot product, the scores become weights through
a softmax, and the query's output is the weighted average of the **value**
vectors. A **mask** says which keys each query may look at: a causal mask stops
a token from seeing later tokens, and a padding mask hides the filler at the end
of a short sequence.

`Q` has `n` rows (queries) and `K` has `m` rows (keys), all of length $d_k$
(`dk`). `V` has `m` rows (one value per key) of length $d_v$ (`dv`).
`mask[i][j]` is `1` if query $i$ may attend to key $j$, and `0` if it may not.
Query $i$ scores key $j$ by $s_{ij}$, turns its scores into weights $w_{ij}$,
and outputs $\text{out}_i$:

$$
\begin{aligned}
s_{ij} &= \frac{Q_i \cdot K_j}{\sqrt{d_k}} \\[1.5ex]
w_{ij} &=
\begin{cases}
  \dfrac{e^{s_{ij}}}{\sum_{k \,:\, \text{mask}_{ik} = 1} e^{s_{ik}}} & \text{if } \text{mask}_{ij} = 1 \\[2ex]
  0 & \text{if } \text{mask}_{ij} = 0
\end{cases} \\[1.5ex]
\text{out}_i &= \sum_{j=1}^{m} w_{ij}\, V_j
\end{aligned}
$$

Each query's weights are a softmax over the keys it may attend to; a blocked
key gets weight exactly `0`, however high its score.

**Return `[output, weights]`**: `output` has `n` rows of `dv` numbers, and
`weights` has `n` rows of `m` numbers.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays are fine as return values.

**Numerical stability matters.** Entries in the tests reach ±100, so a score
can reach the tens of thousands, far past the point (about 709) where `exp`
overflows a float. That includes the scores of blocked keys.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= n, m <= 64` and `1 <= dk, dv <= 32`
- `Q` is `n × dk`, `K` is `m × dk`, `V` is `m × dv`, and `mask` is `n × m`
- Every entry of `Q`, `K` and `V` is a finite number with absolute value `<= 100`
- Every `mask` entry is `0` or `1`, and every row of `mask` contains at least
  one `1`

## Examples

**Example 1**
```
Input:  Q = [[1.0, 0.0]],
        K = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]],
        V = [[10.0], [20.0], [30.0]],
        mask = [[1, 1, 1]]
Output: [[[15.64053899828016]],
         [[0.575975345215362, 0.28399540974126003, 0.14002924504337802]]]
Explanation: the scores are 1/√2, 0 and −1/√2. Their softmax is about
[0.576, 0.284, 0.140], and the output is 0.576·10 + 0.284·20 + 0.140·30.
```

**Example 2**
```
Input:  Q = [[1.0, 1.0], [2.0, 0.0], [0.0, -1.0]],
        K = [[1.0, 0.0], [0.0, 2.0], [1.0, 1.0]],
        V = [[1.0, 0.0, 2.0], [0.0, 1.0, -1.0], [3.0, 3.0, 0.0]],
        mask = [[1, 0, 0], [1, 1, 0], [1, 1, 1]]
Output: [[[1.0, 0.0, 2.0],
          [0.8044296825069569, 0.19557031749304313, 1.4132890475208706],
          [1.427961574439142, 0.9920154742671581, 1.011921445387346]],
         [[1.0, 0.0, 0.0],
          [0.8044296825069569, 0.19557031749304313, 0.0],
          [0.575975345215362, 0.14002924504337802, 0.28399540974126003]]]
Explanation: a causal mask. Query 0 may only attend to key 0, so it copies
V₀. Query 1 sees keys 0 and 1, with scores √2 and 0.
```

**Example 3**
```
Input:  Q = [[3.0, 4.0], [-1.0, 0.5]],
        K = [[3.0, 4.0], [2.0, -2.0], [0.0, 1.0]],
        V = [[100.0, 0.0], [0.0, 1.0], [5.0, 5.0]],
        mask = [[0, 1, 1], [1, 1, 0]]
Output: [[[4.929169820616558, 4.943335856493246],
          [80.44296825069569, 0.19557031749304313]],
         [[0.0, 0.014166035876688408, 0.9858339641233116],
          [0.8044296825069569, 0.19557031749304313, 0.0]]]
Explanation: query 0 matches key 0 best (score 25/√2 ≈ 17.7), but that key
is blocked, so its weight is 0 and query 0 never sees the value 100.
```
