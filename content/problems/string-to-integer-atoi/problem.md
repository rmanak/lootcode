Convert the string `s` to a 32-bit signed integer (like C's `atoi`):

1. Skip leading spaces (`' '` is the only whitespace considered).
2. Read an optional single `'+'` or `'-'` sign.
3. Read the following digits until a non-digit character (or the end) is reached.
4. Anything after the digits is ignored.

If no digits were read, return `0`. Clamp the result to the 32-bit signed range
`[-2^31, 2^31 - 1]`: values below `-2^31` become `-2^31` (`-2147483648`) and values
above `2^31 - 1` become `2^31 - 1` (`2147483647`).

**Examples**
```
s = "42"             ->  42
s = "   -42"         ->  -42
s = "4193 with words"->  4193
s = "words and 987"  ->  0
s = "-91283472332"   ->  -2147483648
```

**Constraints:** `0 <= len(s) <= 200`, `s` consists of digits, letters, `' '`,
`'+'` and `'-'`.
