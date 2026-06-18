Count strings of length `n` made of vowels `a, e, i, o, u` obeying: after `a` comes
`e`; after `e` comes `a` or `i`; after `i` comes anything except `i`; after `o`
comes `i` or `u`; after `u` comes `a`. **Return the count, modulo `10^9 + 7`.**

**Examples**
```
n = 1  ->  5
n = 2  ->  10
n = 5  ->  68
```

**Constraints:** `1 <= n <= 2*10^4`.
