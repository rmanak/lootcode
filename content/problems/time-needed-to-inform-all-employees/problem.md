A company tree has `n` employees; `manager[i]` is `i`'s manager (`-1` for the head).
Employee `i` takes `informTime[i]` minutes to inform all direct subordinates. **Return
the number of minutes until everyone is informed**, starting from `headID`.

**Examples**
```
n=6, headID=2, manager=[2,2,-1,2,2,2], informTime=[0,0,1,0,0,0]  ->  1
n=7, headID=6, manager=[1,2,3,4,5,6,-1], informTime=[0,6,5,4,3,2,1]  ->  21
```

**Constraints:** `1 <= n <= 10^5`, valid tree, `0 <= informTime[i] <= 1000`.
