Item `i` has value `values[i]` and label `labels[i]`. Choose a subset with at most
`numWanted` items and at most `useLimit` items per label, to **maximize the sum of
values.** Return that maximum sum.

**Examples**
```
values=[5,4,3,2,1], labels=[1,1,2,2,3], numWanted=3, useLimit=1  ->  9
values=[5,4,3,2,1], labels=[1,3,3,3,2], numWanted=3, useLimit=2  ->  12
values=[9,8,8,7,6], labels=[0,0,0,1,1], numWanted=3, useLimit=1  ->  16
```

**Constraints:** `1 <= len(values) == len(labels) <= 2*10^4`,
`0 <= values[i], labels[i] <= 2*10^4`, `1 <= numWanted, useLimit <= len(values)`.
