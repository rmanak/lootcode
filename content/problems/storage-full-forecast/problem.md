A storage array samples how full each volume is and warns the administrator
days before one runs out of space. The forecast is a **linear regression** of
used bytes against time, fitted over a sliding window of recent samples so
that it adapts when the growth rate changes. Implement it.

- `StorageForecaster(windowSize)`: the fit uses only the most recent
  `windowSize` samples.
- `recordUsage(timestamp, usedBytes)` records a sample. `timestamp` is in Unix
  seconds, and timestamps strictly increase from call to call.
- `forecastFull(totalBytes)` returns the time at which the fitted line reaches
  `totalBytes`, or `-1` if there are fewer than $2$ samples in the window or
  the fitted usage is flat or shrinking (slope $\le 0$).
- `getGrowthRatePerDay()` returns the fitted slope in bytes per day
  ($86400$ seconds), or $0$ with fewer than $2$ samples.

**The fit.** Over the $n$ samples $(t_i, y_i)$ in the window, with means
$\bar t$ and $\bar y$, the least-squares line has slope

$$
b = \frac{\sum_i (t_i - \bar t)(y_i - \bar y)}{\sum_i (t_i - \bar t)^2}
$$

and passes through $(\bar t, \bar y)$. It reaches `totalBytes` at
$\bar t + (\texttt{totalBytes} - \bar y) / b$, which may be in the past if the
volume is already over the line.

**Precision.** Unix timestamps are about $1.7 \times 10^9$, and byte counts run
to $10^{13}$. The textbook form
$b = \frac{n \sum t y - \sum t \sum y}{n \sum t^2 - (\sum t)^2}$ subtracts
numbers near $10^{22}$ that agree in nearly every digit, and in floating
point it can return garbage, even a slope of the wrong sign. Center the data
first, as above. The tests promise that whenever a forecast or rate is
requested, the slope is either exactly $0$ (in exact arithmetic) or far from
$0$ relative to the data.

Answers are accepted within a relative error of $10^{-6}$.

You may use **numpy** and the Python standard library.

## Constraints

- `2 <= windowSize <= 500`
- `0 <= timestamp <= 4·10⁹`, strictly increasing; `0 <= usedBytes, totalBytes <= 10¹³`
- At most `3000` calls in total

## Examples

**Example 1**

```
Input
["StorageForecaster", "recordUsage", "recordUsage", "recordUsage", "forecastFull", "getGrowthRatePerDay"]
[[10], [0, 100000000000], [86400, 110000000000], [172800, 120000000000], [200000000000], []]

Output
[null, null, null, null, 864000.0, 10000000000.0]
```

Explanation: usage grows 10 GB a day from 100 GB, so it reaches 200 GB after
10 days (864000 s).

**Example 2**

```
Input
["StorageForecaster", "forecastFull", "recordUsage", "getGrowthRatePerDay", "recordUsage", "forecastFull",
 "recordUsage", "recordUsage", "forecastFull", "recordUsage", "getGrowthRatePerDay", "forecastFull"]
[[3], [5000], [1000, 900], [], [2000, 700], [5000], [3000, 700], [4000, 700], [5000], [5000, 1000], [], [5000]]

Output
[null, -1, null, 0.0, null, -1, null, null, -1, null, 12960.0, 32000.0]
```

Explanation: with no samples, or one, there is no line. Usage then falls (‑1),
and then the window of 3 holds three equal samples (flat, ‑1). Finally the
window is (3000, 700), (4000, 700), (5000, 1000): the slope is
300000 / 2000000 = 0.15 bytes per second, 12960 per day, and the line
through (4000, 800) reaches 5000 bytes at 4000 + 4200 / 0.15 = 32000.

**Example 3**

```
Input
["StorageForecaster", "recordUsage", "recordUsage", "recordUsage", "recordUsage", "forecastFull", "recordUsage",
 "forecastFull", "forecastFull"]
[[4], [0, 0], [1, 10], [2, 10], [3, 30], [100], [4, 40], [100], [0]]

Output
[null, null, null, null, null, 11.222222222222221, null, 9.545454545454545, 0.45454545454545453]
```

Explanation: the first fit has slope 45 / 5 = 9 through (1.5, 12.5). The fifth
sample pushes (0, 0) out of the window, and the slope becomes 11 through
(2.5, 22.5). The last call asks when the line was at 0, which lies in the past.
