Let `f(x)` be the number of trailing zeroes of `x!`. Given `K`, return how many
non-negative integers `x` satisfy `f(x) == K`. (The answer is always `0` or `5`.)

**Examples**
```
K = 0   ->  5   (0!, 1!, 2!, 3!, 4! all end in 0 zeroes)
K = 5   ->  0   (no x! ends in exactly 5 zeroes)
```

**Constraints:** `0 <= K <= 10^9`.
