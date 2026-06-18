On an `m x n` grid of heights, the Pacific touches the top/left edges and the
Atlantic the bottom/right. Water flows to an equal-or-lower neighbour (N/S/E/W).
Return all cells `[r, c]` from which water can reach **both** oceans, in **any
order** (each cell stays as `[row, col]`).

**Constraints:** `1 <= m, n <= 200`, `0 <= heights[r][c] <= 10^5`.
