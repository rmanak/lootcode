One bad batch can produce a huge gradient, and a single step along it can
wreck a model. **Clipping by global norm** guards against this. It treats
every parameter's gradient as one long vector and, when that vector is too
long, shrinks all of them by the same factor. Their direction does not change.

`grads` is a list of gradient tensors, each flattened to a list of numbers.
The tensors can have different lengths. Write $g_{t,k}$ for entry $k$ of
tensor $t$, $G$ for `globalNorm` and $\tau$ for `maxNorm`:

$$
G = \sqrt{\sum_{t} \sum_{k} g_{t,k}^2}
$$

and every entry of every tensor is clipped the same way:

$$
g_{t,k} \leftarrow
\begin{cases}
g_{t,k} \cdot \dfrac{\tau}{G} & \text{if } G > \tau \\[1ex]
g_{t,k} & \text{otherwise}
\end{cases}
$$

After clipping, the global norm is at most $\tau$.

**Return `[clippedGrads, globalNorm]`**, where `clippedGrads` has the same
shape as `grads` and `globalNorm` is the norm $G$ **before** clipping.

**Stability.** Exploding gradients really do explode: entries can be as large
as $10^{200}$. Squaring one gives `inf`, so a plain sum of squares fails.
Scale first, for example by dividing every entry by the largest magnitude
before squaring and multiplying it back afterwards. `torch.linalg.vector_norm`
does not do this for you: on such entries it returns `inf` too.

Write it in **PyTorch** (`torch` is already imported). `grads` arrives as a list
of float64 tensors and `maxNorm` as a plain Python value. Return the structure
described above with a tensor in place of each list of numbers and a 0-dim
tensor in place of each single number (float64; int64 for integers). The
examples print tensors as nested lists. These built-ins would do the exercise
for you and raise if called: `torch.nn.utils.clip_grad_norm_`,
`torch.nn.utils.clip_grad_norm`, `torch.nn.utils.clip_grad.clip_grad_norm_`,
`torch.nn.utils.clip_grad.clip_grad_norm`, `torch.nn.utils.get_total_norm`,
`torch.nn.utils.clip_grads_with_norm_`.

Your answer is checked against the reference implementation with
`torch.allclose` semantics (`rtol=1e-5`, `atol=1e-6`), and every tensor's shape
and dtype must match exactly. Besides the stored tests, every run adds 5 hidden
tests drawn at random within the constraints.

**Why float64?** Training usually runs in float32, but the entries here reach
$10^{200}$, and float32 tops out near $3.4 \times 10^{38}$. float32 overflows
much sooner, too: squaring any entry above about $1.8 \times 10^{19}$ already
gives `inf`, so the same scaling trick matters there.

## Constraints

- `1 <= len(grads) <= 50`, every tensor has at least one entry, and there are
  at most `10⁴` entries in total
- Every entry is finite with absolute value `<= 1e200`
- `0 < maxNorm <= 10⁶`

## Examples

**Example 1**
```
Input:  grads = [[3.0], [4.0]], maxNorm = 1.0
Output: [[[0.6000000000000001], [0.8]], 5.0]
Explanation: the global norm is sqrt(9 + 16) = 5, so both tensors are scaled
by 1/5. Clipping each tensor on its own would leave 3 → 1 and 4 → 1, which
changes the direction.
```

**Example 2**
```
Input:  grads = [[1.0, -2.0], [2.0]], maxNorm = 5.0
Output: [[[1.0, -2.0], [2.0]], 3.0]
Explanation: the norm is 3, which is already within maxNorm, so nothing
changes.
```

**Example 3**
```
Input:  grads = [[6.0, 0.0, -8.0], [0.0], [0.0, 0.0]], maxNorm = 5.0
Output: [[[3.0, 0.0, -4.0], [0.0], [0.0, 0.0]], 10.0]
```
