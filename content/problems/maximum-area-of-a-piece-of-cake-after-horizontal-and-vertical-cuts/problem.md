A cake is `h` tall and `w` wide. `horizontalCuts[i]` is the distance from the top to
a horizontal cut; `verticalCuts[j]` is the distance from the left to a vertical cut.
After all cuts, **return the area of the largest piece**, modulo `10^9 + 7`. The
largest piece is the largest gap between consecutive horizontal cuts (including the
borders) times the largest such vertical gap.

**Examples**
```
h=5, w=4, horizontalCuts=[1,2,4], verticalCuts=[1,3]  ->  4
h=5, w=4, horizontalCuts=[3,1],  verticalCuts=[1]     ->  6
h=5, w=4, horizontalCuts=[3],    verticalCuts=[3]     ->  9
```

**Constraints:** `2 <= h, w <= 10^9`, cuts are distinct and strictly inside the
cake. (Take the max gap product before applying the modulo.)
