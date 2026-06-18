`A` is a list of equal-length strings. Choosing a set of column indices to delete
from every string, **return the minimum number of columns to delete so that every
remaining row is in non-decreasing order.**

**Examples**
```
A = ["babca","bbazb"]  ->  3
A = ["edcba"]          ->  4
A = ["ghi","def","abc"] ->  0
```

**Constraints:** `1 <= len(A) <= 100`, `1 <= len(A[i]) <= 100`, lowercase letters.
