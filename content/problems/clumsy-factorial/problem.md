The *clumsy factorial* of `N` takes `N, N-1, ..., 1` and cycles the operators
`* / + -` between them (e.g. `clumsy(10) = 10*9/8+7-6*5/4+3-2*1`), using normal
operator precedence and **floor-toward-zero division**. **Return `clumsy(N)`.**

**Examples**
```
N = 4   ->  7    (4*3/2 + 1)
N = 10  ->  12
```

**Constraints:** `1 <= N <= 10^4`.
