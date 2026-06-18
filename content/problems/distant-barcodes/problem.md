You are given a list `barcodes`. Return `true` if and only if the barcodes can be
rearranged so that **no two adjacent barcodes are equal** (otherwise `false`).

Such a rearrangement exists exactly when no single value occurs too often: it is
possible iff the most frequent value appears at most `(len(barcodes) + 1) // 2`
times.

**Examples**
```
barcodes = [1,1,1,2,2,2]    ->  true   (e.g. [1,2,1,2,1,2])
barcodes = [1,1,1,1,2,2,3]  ->  false  (value 1 appears 4 > (7+1)//2 = 4? no -> ...)
barcodes = [1,2]            ->  true
```

**Constraints:** `1 <= len(barcodes) <= 10^4`, `1 <= barcodes[i] <= 10^4`.
