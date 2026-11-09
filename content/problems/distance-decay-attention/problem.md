Instead of adding position embeddings to the tokens, **ALiBi** (Attention with
Linear Biases) tells attention about word order directly: every score is
penalized in proportion to how far apart the two tokens are, so each head
prefers nearby tokens. Different heads use different penalty slopes, which
lets some heads look locally and others far away. Implement multi-head
attention with this bias.

`Q`, `K` and `V` are $n \times D$: one row per token, already projected. The
number of heads $H$ is `len(slopes)`, and $D$ is a multiple of $H$. Head $h$
(counting from $0$) uses the columns $h\,d_h$ to $(h+1)\,d_h - 1$ of each
matrix, where $d_h = D / H$; write $Q^{(h)}, K^{(h)}, V^{(h)}$ for those
slices. With $\alpha_h$ = `slopes[h]`, head $h$ computes

$$
\begin{aligned}
S^{(h)}_{ij} &= \frac{Q^{(h)}_i \cdot K^{(h)}_j}{\sqrt{d_h}} - \alpha_h\, |i - j| \\[1ex]
A^{(h)}_{ij} &= \frac{e^{S^{(h)}_{ij}}}{\sum_k e^{S^{(h)}_{ik}}} \\[1ex]
O^{(h)} &= A^{(h)} V^{(h)}
\end{aligned}
$$

where the sum runs over the keys token $i$ may attend to: all $n$ of them, or
only $j \le i$ when `causal` is true. The output is the heads' outputs side by
side, $O = [\,O^{(0)}\; O^{(1)} \cdots O^{(H-1)}\,]$, again $n \times D$. (There
is no output projection.)

Scores in the tests reach the hundreds and slopes reach $50$, so compute each
softmax stably.

**Return** $O$.

You may use **numpy** and the Python standard library. A numpy array is fine
as the return value.

## Constraints

- `1 <= n <= 64` and `1 <= D <= 64`
- `1 <= len(slopes) <= 8`, and `D` is a multiple of `len(slopes)`
- Every entry of `Q`, `K` and `V` is finite with absolute value `<= 30`
- Every slope is in `[0, 50]`

## Examples

**Example 1**
```
Input:  Q = [[0.0], [0.0], [0.0]], K = [[0.0], [0.0], [0.0]], V = [[1.0], [2.0], [4.0]], slopes = [1.0],
        causal = false
Output: [[1.5148201905659389], [2.2119415576170853], [3.240451338379263]]
Explanation: every dot product is 0, so only the bias matters. Token 0 weights
the three values by 1, e⁻¹ and e⁻², which gives (1 + 2e⁻¹ + 4e⁻²) / (1 + e⁻¹ + e⁻²) ≈ 1.515.
Each token leans toward its own value.
```

**Example 2**
```
Input:  Q = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], K = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
        V = [[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]], slopes = [0.0, 2.0], causal = true
Output: [[1.0, 10.0], [1.5, 19.525741268224333], [2.0, 28.697008446611846]]
Explanation: two heads of width 1: head 0 owns column 0 and head 1 column 1.
Token 0 can only see itself. Head 0 has slope 0 and its queries in column 0
are 1, 0, 1. Token 1's query is 0 there, so it averages the values 1 and 2.
Head 1's steep slope keeps token 1 close to its own value 20.
```

**Example 3**
```
Input:  Q = [[2.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]], K = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [2.0, 0.0]],
        V = [[1.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 1.0]], slopes = [0.5], causal = false
Output: [[0.17392783328926004, 0.6565951291288034], [0.2350037122015945, 0.14253695659655094],
         [0.14253695659655094, 0.2350037122015945], [0.1015363240915518, 0.45505423392341127]]
Explanation: one head of width 2. Token 0 matches key 3 strongly (score
4/√2 ≈ 2.83), and even after the distance penalty 0.5·3 = 1.5 that key gets
most of its attention. The other queries are zero, so their weights depend
only on distance.
```
