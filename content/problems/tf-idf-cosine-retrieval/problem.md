Before dense embeddings, search ran on **TF-IDF**, and it is still the
keyword half of most hybrid retrieval systems. Build a tiny search engine:
index `documents`, then return the `k` best matches for each query.

**Tokenize** by lowercasing and taking every maximal run of letters and
digits, `re.findall(r"[a-z0-9]+", text.lower())`. So `"Banana!"` is the token
`banana`, and `"don't"` becomes `don` and `t`. There is no stemming, so
`rank` and `ranking` are different tokens.

**Weights.** With $N$ documents, let $\operatorname{df}(t)$ be the number of
documents that contain token $t$. Use the smoothed IDF that scikit-learn uses
by default:

$$
\operatorname{idf}(t) = \ln \frac{1 + N}{1 + \operatorname{df}(t)} + 1
$$

A text's vector $v$ has one weight per token $t$ in the vocabulary (the tokens
of the documents), $v_t = \operatorname{tf}(t) \cdot \operatorname{idf}(t)$,
where $\operatorname{tf}(t)$ is the count of $t$ in the text. Then the vector
is divided by its Euclidean length, $\hat v = v / \lVert v \rVert$. Query
tokens that never occur in any document are ignored, and the IDF comes from
the documents alone. A text whose vector is all zeros (no known tokens) stays
all zeros.

**Score** each document by the dot product $\hat q \cdot \hat d$ of the
normalized query and document vectors, which is their **cosine similarity**.
It is $0$ whenever either vector is all zeros.

For each query, rank all documents by score, highest first, with **ties broken
by the smaller document index**. Keep the first `k`. Documents that score $0$
still count, so there are always exactly `k` results.

**Return `[topIndices, topScores]`**: for each query, the list of the `k`
document indices, and the list of their scores in the same order.

You may use the Python standard library and **numpy**.

Indices must match exactly. Scores are accepted within a relative `1e-6` (or
an absolute `1e-9`). Within each query's top $k + 1$ documents, two scores are
either exactly equal or differ by more than a relative `1e-9`. Exact ties come
from documents with identical token counts, or from scores of exactly 0.

## Constraints

- `1 <= len(documents) <= 200`, each at most `1000` printable ASCII
  characters (possibly empty)
- `1 <= len(queries) <= 20`, each at most `200` printable ASCII characters
- `1 <= k <= len(documents)`

## Examples

**Example 1**
```
Input:  documents = ["the cat sat", "the dog sat", "a cat and a dog"], queries = ["cat"], k = 2
Output: [[[0, 2]], [[0.5773502691896257, 0.3065042162415877]]]
Explanation: "cat" appears in 2 of the 3 documents, so idf(cat) = ln(4/3) + 1.
Document 0 is shorter, so the token makes up more of its normalized vector
than of document 2's.
```

**Example 2**
```
Input:  documents = ["Deep learning, deep models.", "Learning to rank documents", "Models of the world"],
        queries = ["deep models", "ranking"], k = 3
Output: [[[0, 2, 1], [0, 1, 2]], [[0.9037569318498992, 0.2433744620017139, 0.0], [0.0, 0.0, 0.0]]]
Explanation: "ranking" is not a token of any document ("rank" is), so the
second query's vector is all zeros. Every score is 0, and the order falls back
to the document index.
```

**Example 3**
```
Input:  documents = ["apple banana", "banana banana", "cherry", "banana apple"],
        queries = ["Banana!", "apple pie"], k = 3
Output: [[[1, 0, 3], [0, 3, 1]], [[1.0, 0.6292275146695526, 0.6292275146695526], [0.7772211620785797, 0.7772211620785797, 0.0]]]
Explanation: documents 0 and 3 have the same token counts, so they tie, and
the smaller index comes first. "pie" is unknown and is ignored.
```
