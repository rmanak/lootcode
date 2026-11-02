A language model generates text one token at a time. **Greedy decoding** always
takes the single most likely next token, which can paint it into a corner.
**Beam search** keeps the `beamWidth` best partial sequences (the *beam*) at
every step instead, so a sequence with a weak first token can still win.

The "model" here is a **bigram table**: `logProbs[a][b]` is the log-probability
(a number $\le 0$) that token `b` follows token `a`. Tokens are
$0, \dots, V - 1$. A sequence's **score** is the sum of the log-probabilities of
its tokens, each given the token before it. The first generated token follows
`startToken`, which is not part of the output. So with $t_0$ = `startToken`,
the generated tokens $t_1, \dots, t_n$ score

$$
\operatorname{score}(t_1, \dots, t_n) = \sum_{i=1}^{n} \texttt{logProbs}[t_{i-1}][t_i]
$$

There is no length normalization. (Use the table as given; its rows need not
sum to exactly 1 as probabilities.)

Run beam search exactly like this:

1. Start with one live hypothesis: no tokens yet, score $0$.
2. **Expand** every live hypothesis by every token $0, \dots, V - 1$, adding
   that token's log-probability to the score. This gives the candidates.
3. **Rank** the candidates: higher score first. Equal scores are ordered by
   their token lists, **lexicographically smaller first**.
4. **Keep** the top `beamWidth` candidates (all of them if there are fewer).
   A kept candidate whose last token is `eosToken` is **finished** and is never
   expanded again. The other kept candidates are the new live hypotheses.
5. Repeat from step 2 until there are no live hypotheses, or until `maxLen`
   steps have been done. Live hypotheses left after the last step also count as
   finished.

The answer is the finished hypothesis with the **highest score**. Equal scores
go to the lexicographically smaller token list (a list that is a prefix of
another counts as smaller).

**Return `[tokens, score]`**: the answer's generated tokens (including the final
`eosToken`, if it has one) and its score.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists.

The score is accepted when it is within a relative `1e-6` (or an absolute
`1e-9`) of the expected value. The tokens must match exactly.

## Constraints

- `2 <= V <= 50`, and `logProbs` is a `V × V` table
- Every entry of `logProbs` is a finite number with `-100 <= entry <= 0`
- `0 <= startToken, eosToken < V` (they may be the same token)
- `1 <= beamWidth <= 10`
- `1 <= maxLen <= 20`

## Examples

In all three examples token `0` is the start token, `1` and `2` are words
"A" and "B", and `3` is the end-of-sequence token.

**Example 1**
```
Input:  logProbs = [[-9.0, -0.5, -1.0, -3.0],
                    [-9.0, -1.5, -1.5, -0.7],
                    [-9.0, -2.0, -2.0, -0.05],
                    [-9.0, -1.0, -1.0, -1.0]],
        startToken = 0, eosToken = 3, beamWidth = 2, maxLen = 3
Output: [[2, 3], -1.05]
Explanation: step 1 keeps A (−0.5) and B (−1.0). In step 2 the two best
candidates are B EOS (−1.05) and A EOS (−1.2); both finish and nothing is left
alive. Greedy decoding would commit to A and end with A EOS at −1.2.
```

**Example 2**
```
Input:  logProbs = [[-9.0, -0.2, -2.0, -1.5],
                    [-9.0, -0.9, -3.0, -1.4],
                    [-9.0, -1.0, -1.0, -1.0],
                    [-9.0, -1.0, -1.0, -1.0]],
        startToken = 0, eosToken = 3, beamWidth = 2, maxLen = 3
Output: [[3], -1.5]
Explanation: step 1 keeps A (−0.2) and the finished EOS (−1.5). Step 2 keeps
A A (−1.1) and the finished A EOS (−1.6). Step 3 keeps A A A (−2.0) and
A A EOS (−2.5), and stops at maxLen, so A A A counts as finished too. Ending
right away at −1.5 has the highest score.
```

**Example 3**
```
Input:  logProbs = [[-9.0, -1.0, -1.0, -2.0],
                    [-9.0, -2.0, -0.5, -3.0],
                    [-9.0, -0.5, -2.0, -3.0],
                    [-9.0, -1.0, -1.0, -1.0]],
        startToken = 0, eosToken = 3, beamWidth = 2, maxLen = 4
Output: [[1, 2, 1, 2], -2.5]
Explanation: A and B tie at every step, so the beam holds A B A … and
B A B … side by side. After 4 steps, A B A B and B A B A both score −2.5, and
the lexicographically smaller [1, 2, 1, 2] wins.
```
