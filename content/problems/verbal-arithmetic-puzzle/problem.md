Each distinct letter maps to a distinct digit `0`-`9`; every word (and `result`) is
read as a number with **no leading zero** (a single-letter word may be `0`). **Return
`true` if the letters can be assigned so that the `words` sum to `result`.**

**Examples**
```
words = ["SEND","MORE"], result = "MONEY"          ->  true
words = ["SIX","SEVEN","SEVEN"], result = "TWENTY"  ->  true
words = ["LEET","CODE"], result = "POINT"          ->  false
```

**Constraints:** `2 <= len(words) <= 5`, `1 <= len(words[i]), len(result) <= 7`,
uppercase letters, at most 10 distinct letters overall.
