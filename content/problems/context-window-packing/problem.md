A retrieval-augmented assistant has ranked documents to put into the model's
prompt, but the prompt has a **token budget**. Each document has a relevance
score and a length in tokens. Choose what to include so that the total score
is as large as possible.

`documents[k]` is `[docId, score, tokens]`, in ranked order. Answer two
versions of the problem:

1. **Whole documents only.** Choose a subset whose token counts sum to at
   most `budget`, maximizing the sum of their scores. (Including the documents
   in their original order is what the prompt does; it doesn't change the
   score.)
2. **One truncated document.** As in part 1, but you may additionally include
   **one** more document cut short. It is the last thing in the prompt, so it
   must come **after** every whole document chosen, in the original order. A
   document of $T$ tokens and score $s$, cut to $t$ tokens with
   $\texttt{minTokens} \le t \le T$, contributes $s \cdot t / T$. Whole and
   truncated tokens together must fit in `budget`. Including no truncated
   document is allowed, so this answer is at least the part-1 answer.

**Return `[best1, best2]`**, the two maximum total scores.

$n$ can reach $200$ and the budget $2 \cdot 10^4$, so trying subsets is out of
the question; think of 0/1 knapsack. For part 2, it helps to know, for every
prefix of the documents and every exact token total, the best whole-document
score.

## Constraints

- `1 <= n <= 200`, `1 <= budget <= 20000`, `1 <= minTokens <= 2000`
- Every `tokens` is an integer in `[1, 2000]`; every `score` a number in `[0, 1000]`
- Document ids are distinct strings

## Examples

**Example 1**
```
Input:  budget = 100, minTokens = 20, documents = [["d1", 9.0, 60], ["d2", 8.5, 50], ["d3", 7.0, 30], ["d4", 6.0, 20]]
Output: [21.5, 21.5]
Explanation: d2, d3 and d4 fill the 100 tokens exactly for 8.5 + 7 + 6 = 21.5.
The best document, d1, is not in the best set. No room is left to truncate
anything.
```

**Example 2**
```
Input:  budget = 95, minTokens = 20, documents = [["d1", 9.0, 60], ["d2", 8.5, 50], ["d3", 6.0, 40]]
Output: [14.5, 14.95]
Explanation: with whole documents, d2 + d3 (90 tokens) score 14.5. With
truncation, d1 whole leaves 35 tokens, and d2 cut to 35 tokens adds
8.5 · 35/50 = 5.95, for 14.95. (Keeping d2 whole and cutting d1 to 45 tokens
would score 15.25, but d1 comes before d2, so it cannot be the cut-off last
document.)
```

**Example 3**
```
Input:  budget = 90, minTokens = 40, documents = [["d1", 7.0, 10], ["d2", 1.0, 60], ["d3", 6.0, 50], ["d4", 5.0, 40]]
Output: [13.0, 13.0]
Explanation: d1 + d3 score 13 with 60 tokens. Taking documents by score per
token (d1, then d4) stops at 12. With truncation, the 30 tokens left after
d1 + d3 are fewer than minTokens, so d4 cannot be added even in part.
```
