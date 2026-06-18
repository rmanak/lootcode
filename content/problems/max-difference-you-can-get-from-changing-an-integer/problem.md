Apply this operation **twice independently** to `num`: pick a digit `x` and a digit
`y`, and replace every `x` with `y`. The result must have no leading zero and not be
`0`. Let `a` and `b` be the two results. **Return the maximum value of `a - b`.**

**Examples**
```
num = 555     ->  888   (a = 999, b = 111)
num = 9       ->  8
num = 123456  ->  820000
num = 10000   ->  80000
```

**Constraints:** `1 <= num <= 10^8`.
