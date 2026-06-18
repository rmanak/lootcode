You roll `d` dice, each with faces `1..f`. **Return the number of ways the faces can
sum to `target`**, modulo `10^9 + 7`.

**Examples**
```
d = 1, f = 6, target = 3   ->  1
d = 2, f = 6, target = 7   ->  6
d = 2, f = 5, target = 10  ->  1
d = 1, f = 2, target = 3   ->  0
```

**Constraints:** `1 <= d, f <= 30`, `1 <= target <= 1000`.
