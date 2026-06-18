A row of colored balls (`board`) sits on the table; you hold more balls (`hand`),
each colored `R`/`Y`/`B`/`G`/`W`. Repeatedly insert one ball from your hand anywhere
in the row; whenever `>= 3` same-colored balls become adjacent they are removed (and
removals cascade). **Return the minimum number of balls you must insert to clear the
board**, or `-1` if it is impossible.

**Examples**
```
board = "WWRRBBWW", hand = "WRBRW"   ->  2
board = "G", hand = "GGGGG"          ->  2
board = "RBYYBBRRB", hand = "YRBGB"  ->  3
board = "WRRBBW", hand = "RB"        ->  -1
```

**Constraints:** `1 <= len(board) <= 16`, `1 <= len(hand) <= 5`, colors in
`RYBGW`.
