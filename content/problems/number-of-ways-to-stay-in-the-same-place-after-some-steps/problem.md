A pointer starts at index `0` of an array of length `arrLen`. At each step it may
move one position left, one position right, or stay — but it must never leave the
array. Return the number of ways the pointer is back at index `0` after exactly
`steps` steps, modulo `10^9 + 7`.

**Examples**
```
steps = 3, arrLen = 2   ->  4
steps = 2, arrLen = 4   ->  2
steps = 4, arrLen = 2   ->  8
```

**Constraints:** `1 <= steps <= 500`, `1 <= arrLen <= 10^6`.
