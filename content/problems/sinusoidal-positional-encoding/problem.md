# Sinusoidal Positional Encoding

Self-attention has no built-in sense of order. The original transformer
("Attention Is All You Need") fixes this by adding a **positional encoding**
to each token's embedding: a vector of sines and cosines whose frequencies
fall geometrically across the dimensions.

For a position $p$ and a width $d$, column $j$ ($0 \le j < d$) of the
encoding belongs to frequency pair $i = \lfloor j / 2 \rfloor$. With $\beta$ =
`base`:

$$
\begin{aligned}
\mathrm{PE}_{p,\,2i} &= \sin\left( \frac{p}{\beta^{2i/d}} \right) \\[1ex]
\mathrm{PE}_{p,\,2i+1} &= \cos\left( \frac{p}{\beta^{2i/d}} \right)
\end{aligned}
$$

Even columns are sines and odd columns are cosines, interleaved, with columns
$2i$ and $2i + 1$ sharing one frequency. The exponent is $2i / d$, with $i$
the **pair** index, not the column index. When $d$ is odd, the last column is
a sine with no cosine partner.

The paper uses $\beta = 10000$. Here `base` is an input.

**Return a matrix with one row per entry of `positions`** (in the given order)
and `d` columns.

You may use **numpy** and the Python standard library. A numpy array is fine
as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= len(positions) <= 100`, and every position is an integer in `[0, 10⁵]`
- `1 <= d <= 128`
- `2 <= base <= 10⁶`

## Examples

**Example 1**
```
Input:  positions = [0, 1, 2], d = 4, base = 10000.0
Output: [[0.0, 1.0, 0.0, 1.0],
         [0.8414709848078965, 0.5403023058681398, 0.009999833334166664, 0.9999500004166653],
         [0.9092974268256817, -0.4161468365471424, 0.01999866669333308, 0.9998000066665778]]
Explanation: the two pairs have frequencies 1 / 10000^0 = 1 and
1 / 10000^(2/4) = 0.01. Position 0 is [sin 0, cos 0, sin 0, cos 0].
```

**Example 2**
```
Input:  positions = [3, 10], d = 6, base = 100.0
Output: [[0.1411200080598672, -0.9899924966004454, 0.6022610340763316, 0.7982992213658409,
          0.13879810108005056, 0.990320699135675],
         [-0.5440211108893698, -0.8390715290764524, 0.8344632077604134, -0.551063657751263,
          0.4476708347189573, 0.8941984252625543]]
```

**Example 3**
```
Input:  positions = [1, 0], d = 5, base = 10000.0
Output: [[0.8414709848078965, 0.5403023058681398, 0.025116222909773774, 0.9996845379152098,
          0.0006309573026154199],
         [0.0, 1.0, 0.0, 1.0, 0.0]]
Explanation: d is odd, so column 4 (pair i = 2) is sin(1 / 10000^(4/5)) with
no cosine after it. The rows follow the order of positions.
```
