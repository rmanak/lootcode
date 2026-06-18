A string is composed of the characters `'L'`, `'R'`, and `'X'`. A move replaces one
occurrence of `"XL"` with `"LX"` (an `L` slides one step left) or one occurrence of
`"RX"` with `"XR"` (an `R` slides one step right). Given `start` and `end`, return
`True` if and only if some sequence of moves turns `start` into `end`.

**Examples**
```
start = "RXXLRXRXL", end = "XRLXXRRLX"   ->  true
start = "XL",        end = "LX"          ->  true
start = "LX",        end = "XL"          ->  false
```

**Constraints:** `1 <= len(start) == len(end) <= 10^4`; both contain only `L`, `R`, `X`.
