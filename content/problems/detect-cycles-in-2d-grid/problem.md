`grid` is given as a list of equal-length strings (each character a cell value).
**Return `true` if there is a cycle of length `>= 4`** made of one repeated value,
moving between 4-directionally adjacent equal cells without immediately revisiting
the previous cell.

**Examples**
```
grid = ["aaaa","abba","abba","aaaa"]  ->  true
grid = ["abb","bzb","bba"]            ->  false
```

**Constraints:** `1 <= len(grid)`, all rows equal length, lowercase letters.
