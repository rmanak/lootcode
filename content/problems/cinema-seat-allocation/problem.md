A cinema has `n` rows numbered `1..n`, each with seats `1..10`. Aisles split a row
into seats `1`, `2..3`, `4..7`, `8..9`, `10`. A four-person family needs four
**adjacent** seats; the only spans that work are `[2,3,4,5]`, `[4,5,6,7]`, and
`[6,7,8,9]`. Given the already-reserved seats `reservedSeats[i] = [row, col]`, return
the maximum number of four-person families that can be seated.

**Examples**
```
n = 3, reservedSeats = [[1,2],[1,3],[1,8],[2,6],[3,1],[3,10]]   ->  4
n = 2, reservedSeats = [[2,1],[1,8],[2,6]]                      ->  2
```

**Constraints:** `1 <= n <= 10^9`, `1 <= len(reservedSeats) <= min(10*n, 10^4)`.
