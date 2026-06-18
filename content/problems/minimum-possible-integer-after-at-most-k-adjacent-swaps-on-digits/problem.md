Given a digit string `num`, you may swap **adjacent** digits at most `k` times.
**Return the smallest integer (as a string)** obtainable. Leading zeros in the
result are allowed.

**Examples**
```
num = "4321", k = 4   ->  "1342"
num = "100", k = 1    ->  "010"
num = "36789", k = 1000 ->  "36789"
```

**Constraints:** `1 <= len(num) <= 3*10^4`, digits only with no leading zero,
`1 <= k <= 10^9`.
