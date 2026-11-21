**CLIP** trains an image encoder and a text encoder together on a batch of $N$
matching (image, caption) pairs. Its objective pulls every image towards its own
caption and away from the other $N - 1$, and every caption towards its own
image. Implement that loss in **PyTorch**.

`image_feat` and `text_feat` are $N \times D$ float32 tensors of raw,
**un-normalized** encoder outputs, and row $i$ of each is a matching pair. Let
$\hat u_i$ and $\hat v_i$ be row $i$ of `image_feat` and of `text_feat` scaled
to unit L2 norm, and let $\tau$ = `temperature`. The logits are cosine
similarities divided by $\tau$, and the loss averages a cross-entropy over the
rows of $S$ and one over its columns, with the matching pair as the target:

$$
\begin{aligned}
S_{ij} &= \frac{\hat u_i \cdot \hat v_j}{\tau} \\[1ex]
\ell_i(A) &= -\log \frac{e^{A_{ii}}}{\sum_{k=1}^{N} e^{A_{ik}}} \\[1ex]
\mathcal{L} &= \frac{1}{2N} \sum_{i=1}^{N} \Big( \ell_i(S) + \ell_i(S^\top) \Big)
\end{aligned}
$$

(The paper learns the scale as $e^{t}$, which is $1/\tau$ here. In this
problem $\tau$ is given.)

**Return $\mathcal{L}$ as a scalar float32 tensor**, i.e. a tensor of shape
`()`. A Python float, a shape `(1,)` tensor or a float64 tensor is a different
answer.

`torch` and `torch.nn.functional` are available. Your result is checked against
the reference implementation with `torch.allclose` semantics (`rtol=1e-5`,
`atol=1e-6`), and its shape and dtype must match exactly. Besides the stored
tests, every run adds 5 hidden tests drawn at random within the constraints.

## Constraints

- `image_feat` and `text_feat` are float32 tensors of the same shape `(N, D)`,
  with `1 <= N <= 64` and `1 <= D <= 128`
- Every entry is finite with absolute value `<= 100`, and every row has an L2
  norm of at least `1e-3`
- `temperature` is a float with `0.01 <= temperature <= 10`

## Examples

**Example 1**
```
Input:  image_feat = tensor([[1., 0.], [0., 1.]]),
        text_feat  = tensor([[1., 0.], [0., 1.]]), temperature = 1.0
Output: tensor(0.3133)
Explanation: S is the identity, so every row and every column is a softmax
over [1, 0] with the 1 as the target: the loss is log(1 + e^(-1)) ≈ 0.31326.
```

**Example 2**
```
Input:  image_feat = tensor([[3., 4.], [0., -2.], [1., 1.]]),
        text_feat  = tensor([[6., 8.], [1., 1.], [0., -5.]]), temperature = 0.5
Output: tensor(2.7611)
Explanation: Pair 0 points the same way once normalized. Image 1 points
exactly along caption 2, not its own caption 1, and image 2 points along
caption 1, so the loss is high.
```

**Example 3**
```
Input:  image_feat = tensor([[0.5, -1.5, 2.]]),
        text_feat  = tensor([[-4., 0., 1.]]), temperature = 0.07
Output: tensor(0.)
Explanation: With one pair, each softmax has a single entry, so both
cross-entropies are log(1) = 0, however dissimilar the pair is.
```
