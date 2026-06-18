Read encoded string `S` left to right onto a tape: a letter is appended; a digit `d`
repeats the entire current tape `d` times. **Return the `K`-th letter (1-indexed) of
the decoded string.**

**Examples**
```
S = "leet2code3", K = 10  ->  "o"
S = "ha22", K = 5         ->  "h"
```

**Constraints:** `2 <= len(S) <= 100`, digits are `2..9`, `S` starts with a letter,
`1 <= K <=` decoded length (`< 2^63`).
