A string of `Q`, `W`, `E`, `R` is **balanced** when each of the four characters
appears exactly `len(s)/4` times. You may replace one contiguous substring with any
string of the same length. **Return the minimum length** of substring you must
replace to make `s` balanced (`0` if it already is).

**Examples**
```
s = "QWER"  ->  0
s = "QQWE"  ->  1
s = "QQQW"  ->  2
s = "QQQQ"  ->  3
```

**Constraints:** `1 <= len(s) <= 10^5`, `len(s)` is a multiple of 4, characters are
only `Q`, `W`, `E`, `R`.
