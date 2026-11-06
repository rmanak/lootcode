**CLIP** learns a shared embedding space for images and text from matching
pairs. In a batch of $N$ pairs, image $i$ should be closer to its own caption
$i$ than to the other $N - 1$ captions, and the other way round. The
objective is the **symmetric InfoNCE loss**. Compute the loss and its
gradients with respect to both sets of raw embeddings.

`U` holds the image embeddings and `V` the text embeddings, both $N \times d$,
and row $i$ of each is a matching pair. With $\tau$ = `temperature`,
L2-normalize every row and form the $N \times N$ similarity logits $S$:

$$
\begin{aligned}
\hat u_i &= \frac{U_i}{\lVert U_i \rVert} \\[1ex]
\hat v_j &= \frac{V_j}{\lVert V_j \rVert} \\[1ex]
S_{ij} &= \frac{\hat u_i \cdot \hat v_j}{\tau}
\end{aligned}
$$

Image $i$ must pick caption $i$ (a softmax along row $i$), and caption $j$
must pick image $j$ (a softmax down column $j$):

$$
\begin{aligned}
L_\text{img} &= -\frac{1}{N} \sum_{i=1}^{N} \log \frac{e^{S_{ii}}}{\sum_j e^{S_{ij}}} \\[1ex]
L_\text{txt} &= -\frac{1}{N} \sum_{j=1}^{N} \log \frac{e^{S_{jj}}}{\sum_i e^{S_{ij}}} \\[1ex]
\texttt{loss} &= \tfrac{1}{2} \left( L_\text{img} + L_\text{txt} \right)
\end{aligned}
$$

**Return `[loss, dU, dV]`**, where `dU` and `dV` are the gradients of `loss`
with respect to the **un-normalized** `U` and `V`, the same shapes as the
inputs. The gradient passes through the normalization. For
$\hat x = x / \lVert x \rVert$, a gradient $g$ on $\hat x$ becomes
$\left(g - \hat x\, (\hat x \cdot g)\right) / \lVert x \rVert$ on $x$, so the
component along $\hat x$ drops out.

**Stability.** $\tau$ can be as small as $0.001$, which puts logits near
$\pm 1000$, past the point where `exp` overflows. Use the max-shifted
log-sum-exp for the log-softmax.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays and numpy scalars are fine as return values.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value.

## Constraints

- `U` and `V` are both `N × d`, with `1 <= N <= 64` and `1 <= d <= 32`
- Every entry is finite with absolute value `<= 10`, and every row has a
  Euclidean norm of at least `0.1`
- `0.001 <= τ <= 10`

## Examples

**Example 1**
```
Input:  U = [[1.0, 0.0], [0.0, 1.0]], V = [[1.0, 0.0], [0.0, 1.0]], temperature = 1.0
Output: [0.3132616875182228, [[0.0, 0.13447071068499755], [0.13447071068499755, 0.0]],
         [[0.0, 0.13447071068499755], [0.13447071068499755, 0.0]]]
Explanation: S is the identity, so each row and each column is a softmax over
[1, 0], and loss = log(1 + e^(−1)). Increasing U₀[1] would tilt image 0
towards the wrong caption, so its gradient is positive.
```

**Example 2**
```
Input:  U = [[2.0, 0.0], [0.0, 3.0]], V = [[1.0, 1.0], [-1.0, 1.0]], temperature = 0.5
Output: [0.3752860486522327, [[0.0, -0.07852293186317996], [0.18335363915339584, 0.0]],
         [[-0.27503045873009374, 0.27503045873009374], [-0.07852293186317993, -0.07852293186317998]]]
Explanation: the lengths 2 and 3 disappear in the normalization. That is why
each dU row is orthogonal to its U row: dU₀ = [0, −0.0785] against
U₀ = [2, 0].
```

**Example 3**
```
Input:  U = [[1.0, 2.0, 0.0], [0.0, 1.0, 1.0], [1.0, 0.0, -1.0]],
        V = [[1.0, 1.0, 0.0], [0.0, 2.0, 1.0], [2.0, 0.0, 0.0]], temperature = 0.1
Output: [0.10630810382889644,
         [[-0.09807619447198995, 0.049038097235995, 0.12260047901762608],
          [0.01946807852223839, -0.042322006531909144, 0.04232200653190912],
          [-0.055955995121153276, 0.10249114544473283, -0.055955995121153256]],
         [[0.09755559152884312, -0.09755559152884317, -0.08400596718904697],
          [0.12261868544729443, 0.06966602987095126, -0.13933205974190246],
          [0.0, 0.05606750042490293, 0.10770212119163014]]]
```
