`n` functions (ids `0..n-1`) run on a single-threaded CPU. `logs` is ordered by
time; each entry is `"id:start:t"` or `"id:end:t"`. `"id:start:t"` means the function
begins at the start of time unit `t`; `"id:end:t"` means it ends at the end of time
unit `t` (so it occupied unit `t`). Functions may call each other (and recurse), and
calls are properly nested.

The **exclusive time** of a function is the number of time units spent in it, not
counting time spent inside functions it called. Return the exclusive time of each
function, indexed by id.

**Example**
```
n = 2
logs = ["0:start:0","1:start:2","1:end:5","0:end:6"]   ->  [3,4]
```

**Constraints:** `1 <= n <= 100`, `1 <= len(logs) <= 500`, timestamps fit in a
32-bit integer.
