A warehouse grid (`m` rows of equal-length strings) uses `'#'` for walls, `'.'` for
floor, `'S'` for the player, `'B'` for the single box, and `'T'` for the target. The
player walks up/down/left/right over floor cells and may **push** the box by standing
on the cell opposite the direction of motion (the cell the box moves into must be
floor). The player cannot walk through the box. Return the minimum number of
**pushes** to bring the box onto the target, or `-1` if impossible.

**Examples**
```
grid = ["######","#T#####","#..B.#","#.##.#","#...S#","######"]   ->  3
grid = ["######","#T#####","#..B.#","####.#","#...S#","######"]   ->  -1
```

**Constraints:** `1 <= m, n <= 20`; exactly one `S`, `B`, and `T`.
