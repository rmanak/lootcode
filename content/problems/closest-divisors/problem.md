Given an integer `num`, consider `num + 1` and `num + 2`. Among all ways to write
either of them as a product of two positive integers, find the pair with the smallest
absolute difference. Return that pair as `[smaller, larger]`.

**Examples**
```
num = 8     ->  [3,3]     (9 = 3 x 3)
num = 123   ->  [5,25]    (125 = 5 x 25)
num = 999   ->  [25,40]   (1000 = 25 x 40)
```

**Constraints:** `1 <= num <= 10^9`.
