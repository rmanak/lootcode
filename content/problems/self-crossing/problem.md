Starting at `(0, 0)` you walk `x[0]` north, `x[1]` west, `x[2]` south, `x[3]` east,
then north again, and so on (turning counter-clockwise each move). **Return `true`
if the path ever crosses or touches itself.**

**Examples**
```
x = [2,1,1,2]  ->  true
x = [1,2,3,4]  ->  false
x = [1,1,1,1]  ->  true
```

**Constraints:** `1 <= len(x) <= 10^5`, `1 <= x[i] <= 10^5`.
