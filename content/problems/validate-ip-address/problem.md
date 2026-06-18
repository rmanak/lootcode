**Return `"IPv4"` if `IP` is a valid IPv4 address, `"IPv6"` if it is a valid IPv6
address, and `"Neither"` otherwise.**

- IPv4: four decimal numbers `0`-`255` separated by dots, with **no leading zeros**
  (`"172.16.254.01"` is invalid).
- IPv6: eight groups of `1`-`4` hexadecimal digits separated by colons. Leading
  zeros within a group are allowed, but `::` (zero compression) and extra leading
  zeros beyond four digits are not.

**Examples**
```
"172.16.254.1"                       ->  "IPv4"
"2001:0db8:85a3:0:0:8A2E:0370:7334"  ->  "IPv6"
"256.256.256.256"                    ->  "Neither"
```

**Constraints:** `IP` has no spaces or special characters.
