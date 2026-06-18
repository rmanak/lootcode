Divide `dividend` by `divisor` **without using multiplication, division, or modulo**,
truncating toward zero. The result is clamped to the signed 32-bit range
`[-2^31, 2^31 - 1]` (return `2^31 - 1` on overflow). **Return the quotient.**

**Examples**
```
dividend = 10, divisor = 3   ->  3
dividend = 7, divisor = -3   ->  -2
```

**Constraints:** both fit in signed 32 bits, `divisor != 0`.
