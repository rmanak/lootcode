Build an expression `x op x op x ...` using only `+ - * /` (usual precedence, no
parentheses, no unary minus). Division yields rationals. **Return the least number of
operators needed for the expression to equal `target`.**

**Examples**
```
x = 3, target = 19          ->  5    (3*3 + 3*3 + 3/3)
x = 5, target = 501         ->  8
x = 100, target = 100000000 ->  3    (100*100*100*100)
```

**Constraints:** `2 <= x <= 100`, `1 <= target <= 2*10^8`.
