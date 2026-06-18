`machines[i]` dresses sit in machine `i` in a row. Each move, you may move one dress
from any number of machines to an adjacent machine (simultaneously). **Return the
minimum number of moves to equalize all machines**, or `-1` if impossible.

**Examples**
```
machines = [1,0,5]  ->  3
machines = [0,3,0]  ->  2
machines = [0,2,0]  ->  -1
```

**Constraints:** `1 <= len(machines) <= 10^4`, `0 <= machines[i] <= 10^5`.
