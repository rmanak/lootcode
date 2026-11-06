Llama, Mistral, Qwen and most modern LLMs encode position with **rotary
position embedding**. Instead of adding a position vector, RoPE rotates each
query and key vector by an angle proportional to its position. The dot
product of a rotated query and a rotated key then depends only on their
*relative* distance.

`x` holds $T$ vectors of even width $d$ (one attention head's queries or
keys), and `positions[t]` is the position of row $t$. During generation with
a KV cache these positions do not start at 0. The coordinates are split into
$d/2$ **pairs**, and pair $i$ ($0 \le i < d/2$) rotates at frequency

$$
\theta_i = \texttt{base}^{-2i / d}
$$

For a row at position $p$, pair $i$ with coordinates $(a, b)$ is rotated by
the angle $p\, \theta_i$:

$$
\begin{aligned}
a' &= a \cos(p\, \theta_i) - b \sin(p\, \theta_i) \\
b' &= a \sin(p\, \theta_i) + b \cos(p\, \theta_i)
\end{aligned}
$$

Implementations disagree on **which coordinates form pair $i$**, so `style`
says which layout to use:

- `"interleaved"`: pair $i$ is coordinates $(2i, 2i + 1)$. This is the
  RoFormer paper and Meta's Llama reference code.
- `"half"`: pair $i$ is coordinates $(i, i + d/2)$. This is the "rotate half"
  layout of Hugging Face Llama and GPT-NeoX.

**Return the rotated $T \times d$ matrix**.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. A numpy array is fine as the return value.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `1 <= T <= 64`, and `d` is even with `2 <= d <= 64`
- Every entry of `x` is finite with absolute value `<= 10`
- `positions` has `T` integers, each in `[0, 10⁵]`
- `2 <= base <= 10⁶`
- `style` is `"interleaved"` or `"half"`

## Examples

**Example 1**
```
Input:  x = [[1.0, 0.0], [1.0, 0.0], [0.0, 2.0]], positions = [0, 1, 2], base = 10000.0, style = "half"
Output: [[1.0, 0.0], [0.5403023058681398, 0.8414709848078965], [-1.8185948536513634, -0.8322936730942848]]
Explanation: with d = 2 there is one pair, with θ₀ = 1, and both styles agree.
Position 0 leaves its row unchanged. Position 1 rotates (1, 0) by 1 radian,
giving (cos 1, sin 1).
```

**Example 2**
```
Input:  x = [[1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0]], positions = [0, 1], base = 100.0, style = "interleaved"
Output: [[1.0, 2.0, 3.0, 4.0], [-1.1426396637476532, 1.922075596544176, 2.585678829246765, 4.279516911052588]]
Explanation: θ = [1, 100^(−1/2)] = [1, 0.1]. At position 1, the pair (1, 2)
turns by 1 radian and the pair (3, 4) by 0.1 radians.
```

**Example 3**
```
Input:  x = [[1.0, 2.0, 3.0, 4.0], [0.5, -1.0, 0.0, 2.0]], positions = [5, 6], base = 100.0, style = "half"
Output: [[3.1604350094526414, -0.1625370306360665, -0.10793771827345966, 4.469181324769897],
         [0.480085143325183, -1.9546205616997492, -0.13970774909946293, 1.086028756424321]]
Explanation: here the pairs are (x₀, x₂) and (x₁, x₃). The positions come from
the input (5 and 6), not from the row numbers.
```
