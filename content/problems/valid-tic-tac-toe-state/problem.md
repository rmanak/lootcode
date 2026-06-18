A Tic-Tac-Toe `board` is a length-3 array of length-3 strings over `' '`, `'X'`,
`'O'`. Return `true` if and only if this position can be reached during a valid
game. `'X'` always moves first, players alternate, marks go only on empty squares,
and the game stops once a row, column, or diagonal is filled with one mark (or the
board is full).

**Examples**
```
board = ["O  ","   ","   "]  ->  false   ('X' must move first)
board = ["XOX"," X ","   "]  ->  false   (too many X's)
board = ["XXX","   ","OOO"]  ->  false   (both cannot win)
board = ["XOX","O O","XOX"]  ->  true
```

**Constraints:** `board` is `3 x 3`; each cell is `' '`, `'X'`, or `'O'`.
