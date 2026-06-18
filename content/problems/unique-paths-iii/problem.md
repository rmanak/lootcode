On a 2D grid, `1` is the start, `2` is the end, `0` is a walkable empty square, and
`-1` is an obstacle. Return the number of 4-directional walks from the start to the
end that step on **every** non-obstacle square exactly once.

**Examples**
```
grid = [[1,0,0,0],[0,0,0,0],[0,0,2,-1]]   ->  2
grid = [[1,0,0,0],[0,0,0,0],[0,0,0,2]]     ->  4
grid = [[0,1],[2,0]]                        ->  0
```

**Constraints:** `1 <= rows * cols <= 20`.
