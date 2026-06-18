Compare a `guess` to a `secret` number (digit strings of equal length). A *bull* is a
digit correct in both value and position; a *cow* is a digit present in the secret but
in the wrong position (each secret digit matches at most one guess digit). **Return
the hint as `"xAyB"`** where `x` is bulls and `y` is cows.

**Examples**
```
secret = "1807", guess = "7810"  ->  "1A3B"
secret = "1123", guess = "0111"  ->  "1A1B"
```

**Constraints:** equal-length digit strings.
