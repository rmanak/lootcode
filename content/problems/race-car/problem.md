Your car starts at position `0` with speed `+1` on an infinite number line and obeys
two instructions:
- `'A'`: `position += speed`, then `speed *= 2`;
- `'R'`: if `speed > 0` set `speed = -1`, else `speed = 1` (position unchanged).

**Return the length of the shortest instruction sequence that ends at position
`target`.**

**Examples**
```
target = 3  ->  2     ("AA": 0 -> 1 -> 3)
target = 6  ->  5     ("AAARA": 0 -> 1 -> 3 -> 7 -> 7 -> 6)
```

**Constraints:** `1 <= target <= 10000`.
