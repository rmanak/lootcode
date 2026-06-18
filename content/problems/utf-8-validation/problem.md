Each integer in `data` contributes its low 8 bits as one byte. **Return `true` if the
bytes form a valid UTF-8 encoding**, where a character is 1-4 bytes: a 1-byte char is
`0xxxxxxx`; an `n`-byte char (n>1) starts with `n` ones then a `0`, followed by `n-1`
continuation bytes `10xxxxxx`.

**Examples**
```
data = [197,130,1]  ->  true
data = [235,140,4]  ->  false
```

**Constraints:** `1 <= len(data) <= 2*10^4`, `0 <= data[i] <= 255` (low 8 bits used).
