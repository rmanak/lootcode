Given a list of 24-hour clock times as `"HH:MM"` strings, return the smallest number
of minutes between any two of them. The clock is circular, so the gap from `23:59`
to `00:00` is `1` minute.

**Example**
```
timePoints = ["23:59","00:00"]  ->  1
```

**Constraints:** `2 <= len(timePoints) <= 2*10^4`; each time is a valid `"HH:MM"`.
