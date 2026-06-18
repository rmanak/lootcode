A chef can cook each dish in `1` unit of time. If a dish is the `t`-th cooked
(1-indexed), its *like-time coefficient* is `t * satisfaction[i]`. The chef may
discard some dishes and cook the rest in whatever sequence is best. **Return the
maximum possible sum of like-time coefficients.**

**Examples**
```
satisfaction = [-1,-8,0,5,-9]  ->  14   (keep -1,0,5: 1*-1 + 2*0 + 3*5)
satisfaction = [4,3,2]         ->  20   (2*1 + 3*2 + 4*3)
satisfaction = [-1,-4,-5]      ->  0    (cook nothing)
```

**Constraints:** `1 <= len(satisfaction) <= 500`, `-10^3 <= satisfaction[i] <= 10^3`.
