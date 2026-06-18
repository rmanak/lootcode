`S` is a string of `'D'` (decrease) and `'I'` (increase) of length `n`. A valid
permutation `P` of `{0, 1, ..., n}` satisfies: `P[i] > P[i+1]` where `S[i] == 'D'`
and `P[i] < P[i+1]` where `S[i] == 'I'`. **Return the number of valid permutations,
modulo `10^9 + 7`.**

**Example**
```
S = "DID"  ->  5
```

**Constraints:** `1 <= len(S) <= 200`, characters `'D'`/`'I'`.
