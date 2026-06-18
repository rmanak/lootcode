For an integer `n`, a base `k >= 2` is a *good base* if every digit of `n` written
in base `k` equals `1`. Given `n` as a decimal string, return the **smallest** good
base of `n`, also as a string.

If `n` written in base `k` is all ones with `L` digits, then
`n = 1 + k + k^2 + ... + k^(L-1)`. A larger number of digits forces a smaller base,
so the smallest good base comes from the longest all-ones representation.

**Examples**
```
n = "13"                   ->  "3"     (13 = 111 in base 3)
n = "4681"                 ->  "8"     (4681 = 11111 in base 8)
n = "1000000000000000000"  ->  "999999999999999999"   (= 11 in that base)
```

**Constraints:** `3 <= n <= 10^18`.
