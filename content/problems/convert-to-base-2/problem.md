**Return the base `-2` (negative two) representation of the non-negative integer
`N`** as a string of `0`s and `1`s, with no leading zeros (except `"0"` itself). The
value of a string `b` is `sum(b[i] * (-2)^(len(b)-1-i))`.

**Examples**
```
N = 2  ->  "110"     ((-2)^2 + (-2)^1 = 4 - 2 = 2)
N = 3  ->  "111"     (4 - 2 + 1 = 3)
N = 4  ->  "100"
```

**Constraints:** `0 <= N <= 10^9`.
