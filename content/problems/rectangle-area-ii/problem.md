You are given axis-aligned `rectangles` where `rectangles[i] = [x1, y1, x2, y2]` are
the bottom-left and top-right corners of the i-th rectangle. Return the **total area**
covered by the union of all rectangles. Because the answer may be large, return it
modulo `10^9 + 7`.

**Examples**
```
rectangles = [[0,0,2,2],[1,0,2,3],[1,0,3,1]]   ->  6
rectangles = [[0,0,1000000000,1000000000]]     ->  49   (10^18 mod (10^9 + 7))
```

**Constraints:** `1 <= len(rectangles) <= 200`, `0 <= xi, yi <= 10^9`.
