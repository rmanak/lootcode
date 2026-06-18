`img1` and `img2` are `n x n` binary matrices. You may translate `img1` (slide it any
number of cells up/down/left/right, no rotation) and place it over `img2`. **Return
the largest number of positions where both have a `1` after some translation.**

**Examples**
```
img1 = [[1,1,0],[0,1,0],[0,1,0]], img2 = [[0,0,0],[0,1,1],[0,0,1]]  ->  3
img1 = [[1]], img2 = [[1]]  ->  1
img1 = [[0]], img2 = [[0]]  ->  0
```

**Constraints:** `1 <= n <= 30`, entries are `0` or `1`.
