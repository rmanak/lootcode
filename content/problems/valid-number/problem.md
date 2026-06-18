**Return `true` if `s` is a valid number.** A valid number may have leading/trailing
spaces, an optional sign, an integer or decimal mantissa (e.g. `"3"`, `"3.5"`,
`".5"`, `"5."`), and an optional exponent `e`/`E` followed by an optional sign and an
integer.

**Examples**
```
"0"     ->  true
" 0.1 " ->  true
"abc"   ->  false
"1 a"   ->  false
"2e10"  ->  true
```

**Constraints:** `1 <= len(s) <= 20`, ASCII characters.
