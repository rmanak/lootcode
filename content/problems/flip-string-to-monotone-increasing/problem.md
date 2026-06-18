A `0`/`1` string is *monotone increasing* if it is some `0`s followed by some `1`s.
**Return the minimum number of flips** (`0`->`1` or `1`->`0`) to make `S` monotone
increasing.

**Examples**
```
S = "00110"     ->  1
S = "010110"    ->  2
S = "00011000"  ->  2
```

**Constraints:** `1 <= len(S) <= 2*10^4`, characters `0`/`1`.
