To pick the next token, a language model turns its **logits** (one score per
token in the vocabulary) into a probability distribution and samples from it.
Three knobs shape that distribution: **temperature** sharpens or flattens it,
**top-k** keeps only the $k$ most likely tokens, and **top-p** (nucleus
sampling) keeps the smallest set of most likely tokens that covers probability
$p$.

Randomness is an input here: instead of calling a random number generator, you
get a number `u` drawn uniformly from $[0, 1)$. Tokens are $0, \dots, V - 1$.
Do the following:

1. **Temperature.** With $z$ = `logits` and $\tau$ = `temperature`, the
   probabilities are $p = \operatorname{softmax}(z / \tau)$, that is
   $p_i = e^{z_i / \tau} / \sum_j e^{z_j / \tau}$.
2. **Rank** the tokens by probability, **most likely first**. Tokens with equal
   probability are ranked by id, **lower id first**.
3. **Top-k.** Keep the first `topK` tokens of the ranking.
4. **Top-p.** Renormalize the probabilities of the kept tokens so they sum to 1.
   Walking down the ranking, keep the shortest prefix whose renormalized
   probabilities add up to **at least** `topP` (at least one token is always
   kept).
5. **Final distribution.** Every token that survived gets its probability
   $p_i$ from step 1, divided by the total over the survivors $S$:
   $p_i / \sum_{j \in S} p_j$. Every other token gets $0$.
6. **Sample.** Walk the final distribution in **token-id order** $0, 1, 2,
   \dots$, keeping a running total, and return the first token whose running
   total is **greater than** `u`.

**Return `[token, finalProbs]`**: the sampled token id and the final
distribution as a list of $V$ numbers.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy values are fine in the return value.

**Numerical stability matters.** A temperature as low as `0.01` scales logits
to the tens of thousands.

The tests keep every running total well away from `topP` (step 4) and from `u`
(step 6), so rounding never decides which token is kept or sampled. Each
probability is accepted when it is within a relative `1e-6` (or an absolute
`1e-9`) of the expected value. The token must match exactly.

## Constraints

- `1 <= V <= 1000`, where `V = len(logits)`
- Every logit is a finite number with absolute value `<= 100`
- `0.01 <= temperature <= 100`
- `1 <= topK <= V`
- `0 < topP <= 1`
- `0 <= u < 1`

## Examples

**Example 1**
```
Input:  logits = [-1.0, -0.7, 1.8, -0.6, 0.4, 2.9], temperature = 2.0,
        topK = 5, topP = 0.83, u = 0.54
Output: [5, [0.0, 0.0, 0.30961302096583354, 0.0, 0.15374927607409447, 0.5366377029600721]]
Explanation: at temperature 2 the probabilities are about
[0.061, 0.071, 0.246, 0.074, 0.122, 0.427], so the ranking is 5, 2, 4, 3, 1, 0.
Top-k drops token 0. Renormalized over the other five, the running totals are
0.454, 0.716, 0.846, …, so top-p keeps tokens 5, 2 and 4. In id order, the
final distribution's running totals are 0.310 (token 2), 0.463 (token 4) and
1.0 (token 5), and the first to exceed 0.54 belongs to token 5.
```

**Example 2**
```
Input:  logits = [1.0, 2.0, 0.0, 2.0], temperature = 0.5, topK = 4, topP = 1.0, u = 0.75
Output: [3, [0.06283993466455375, 0.4643278024895243, 0.008504460356397616, 0.4643278024895243]]
Explanation: no filtering; temperature 0.5 doubles the logits before the
softmax. The running totals in id order are 0.063, 0.527, 0.536, 1.0, so u = 0.75
lands on token 3.
```

**Example 3**
```
Input:  logits = [1.0, 3.0, 3.0, 0.0, 3.0], temperature = 1.0, topK = 2, topP = 0.9, u = 0.3
Output: [1, [0.0, 0.5, 0.5, 0.0, 0.0]]
Explanation: tokens 1, 2 and 4 tie for most likely. The tie goes to the lower
ids, so top-k keeps tokens 1 and 2, and token 4 is dropped.
```
