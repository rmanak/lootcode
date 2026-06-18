A balanced parentheses string is scored by: `()` is `1`; `AB` is `A + B`; `(A)` is
`2 * A`. **Return the score of `S`.**

**Examples**
```
"()"        ->  1
"(())"      ->  2
"()()"      ->  2
"(()(()))"  ->  6
```

**Constraints:** `2 <= len(S) <= 50`, `S` is a balanced string of `(` and `)`.
