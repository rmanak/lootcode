Given an integer `n`, return every simplified fraction strictly between `0` and `1`
whose denominator is at most `n`. A fraction `a/b` is *simplified* when `gcd(a, b)`
is `1`. Each fraction is formatted as `"numerator/denominator"`. The fractions may
be returned **in any order**.

**Examples**
```
n = 2   ->  ["1/2"]
n = 3   ->  ["1/2","1/3","2/3"]
n = 4   ->  ["1/2","1/3","1/4","2/3","3/4"]
n = 1   ->  []
```

**Constraints:** `1 <= n <= 100`.
