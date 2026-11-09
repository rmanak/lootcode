Extractive question answering (and keyphrase highlighting) with a BERT-style
encoder puts a linear head on every token that outputs two logits: how likely
the token is to **start** the answer span, and how likely it is to **end** it.
Implement the two pieces around the encoder: the training loss and the
decoding of a span at inference time.

The batch has $B$ examples of $T$ tokens. `startLogits[b]` and `endLogits[b]`
are the $T$ start and end logits of example $b$, and `goldStarts[b]` $\le$
`goldEnds[b]` are the token positions of its correct span (inclusive).

**Loss.** Softmax each example's start logits over its $T$ positions and take
the cross-entropy of the gold start; do the same for the end. The loss is the
average of the two, averaged over the batch (natural log):

$$
L = \frac{1}{B} \sum_{b=1}^{B} \frac{1}{2} \Big( -\log \operatorname{softmax}(s_b)_{g_b} \; - \; \log \operatorname{softmax}(e_b)_{h_b} \Big)
$$

with $s_b, e_b$ the start and end logits and $g_b, h_b$ the gold positions of
example $b$. Logits reach $\pm 100$, so compute the log-softmax stably.

**Decoding.** For each example, pick the span $(i, j)$ that maximizes
$s_{b,i} + e_{b,j}$ among the **valid** spans: $i \le j$ and
$j - i + 1 \le$ `maxLen`. The gold positions play no part here. If several
valid spans tie for the best score, take the smallest $i$, then the smallest
$j$. (Taking the best start and the best end separately can give an end
before the start, or a span far too long.)

**Return `[L, spans]`**, where `spans[b]` is `[i, j]` for example $b$.

You may use **numpy** and the Python standard library.

## Constraints

- `1 <= B <= 64` and `1 <= T <= 512`
- Every logit is a multiple of `0.125` with absolute value `<= 100`
- `0 <= goldStarts[b] <= goldEnds[b] < T`
- `1 <= maxLen <= T`

## Examples

**Example 1**
```
Input:  startLogits = [[0.0, 2.0, 1.0, 0.0]], endLogits = [[3.0, 0.0, 1.0, 2.0]], goldStarts = [1], goldEnds = [3],
        maxLen = 4
Output: [0.9670007038167169, [[1, 3]]]
Explanation: the best end logit (3, at position 0) comes before the best
start (position 1), so that pair is not a span. The best valid span starts at
1 and ends at 3, with score 2 + 2 = 4.
```

**Example 2**
```
Input:  startLogits = [[0.0, 5.0, 0.0, 0.0, 1.0]], endLogits = [[0.0, 0.0, 0.0, 0.0, 5.0]], goldStarts = [1],
        goldEnds = [2], maxLen = 2
Output: [2.532200368130255, [[4, 4]]]
Explanation: (1, 4) would score 10 but is 4 tokens long. Of the spans of at
most 2 tokens, (4, 4) scores 1 + 5 = 6 and beats (1, 1) and (3, 4) at 5.
```

**Example 3**
```
Input:  startLogits = [[1.0, 1.0, 1.0], [100.0, -100.0, 0.0]], endLogits = [[1.0, 1.0, 1.0], [-100.0, 0.0, 100.0]],
        goldStarts = [0, 1], goldEnds = [2, 2], maxLen = 3
Output: [50.549306144334054, [[0, 0], [0, 2]]]
Explanation: in example 0 every span ties, so the smallest start and end win.
Example 0 contributes log 3 to the loss. Example 1's gold start has logit −100
against a maximum of 100: its start loss is about 200, its end loss about 0,
so it contributes about 100. The batch mean is about 50.55.
```
