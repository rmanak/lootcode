`S` and `T` are non-negative rationals written as `<int>`, `<int>.<frac>`, or
`<int>.<frac>(<repeat>)`, where `(<repeat>)` is the repeating part of the decimal
expansion. **Return `true` if they represent the same number.**

**Examples**
```
S = "0.(52)", T = "0.5(25)"      ->  true
S = "0.1666(6)", T = "0.166(66)" ->  true
S = "0.9(9)", T = "1."           ->  true
```

**Constraints:** parts are digit strings; `IntegerPart` length `1..4`, `NonRepeating`
`0..4`, `Repeating` `1..4`.
