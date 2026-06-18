`seats[i]` is `1` if occupied, `0` if empty (there is at least one of each). You sit
in an empty seat to **maximize the distance to the nearest occupied seat**; return
that maximum distance.

**Examples**
```
seats = [1,0,0,0,1,0,1]  ->  2
seats = [1,0,0,0]        ->  3
seats = [0,1]            ->  1
```

**Constraints:** `2 <= len(seats) <= 2*10^4`, `seats[i]` in `{0,1}`.
