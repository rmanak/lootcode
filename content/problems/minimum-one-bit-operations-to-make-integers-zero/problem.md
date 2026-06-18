Transform an integer `n` into `0` using these operations any number of times:

- flip the rightmost (0th) bit;
- flip bit `i` (for `i >= 1`) **only when** bit `i-1` is `1` and bits `0..i-2` are
  all `0`.

**Return the minimum number of operations** needed.

This equals the inverse Gray code of `n`: `f(n) = n XOR f(n >> 1)`.

**Examples**
```
n = 0    ->  0
n = 3    ->  2
n = 6    ->  4
n = 333  ->  393
```

**Constraints:** `0 <= n <= 10^9`.
