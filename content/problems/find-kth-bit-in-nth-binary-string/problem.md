The binary string `Sn` is built recursively:

- `S1 = "0"`
- `Si = S(i-1) + "1" + reverse(invert(S(i-1)))` for `i > 1`

where `reverse(x)` reverses `x` and `invert(x)` flips every bit (`0<->1`). The first
few are `S1 = "0"`, `S2 = "011"`, `S3 = "0111001"`, `S4 = "011100110110001"`.

Return the `k`-th bit of `Sn` (1-indexed) as the string `"0"` or `"1"`. It is
guaranteed that `k` is valid for the given `n`.

**Examples**
```
n = 3, k = 1   ->  "0"
n = 4, k = 11  ->  "1"
n = 1, k = 1   ->  "0"
n = 2, k = 3   ->  "1"
```

**Constraints:** `1 <= n <= 20`, `1 <= k <= 2^n - 1`.
