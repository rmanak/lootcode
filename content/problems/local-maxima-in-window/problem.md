Peak detection in a sensor stream (or in a training-loss curve, or a
spectrogram) usually asks for more than "bigger than both neighbours": a peak
must **rise steadily** into its top and **fall steadily** after it.

Given the integer signal `rawData` and a radius `localArea`, return every
index $i$ such that

- the values strictly increase over the `localArea` positions **leading up**
  to $i$: $\texttt{rawData}[i-m] < \dots < \texttt{rawData}[i-1] < \texttt{rawData}[i]$,
  where $m = \min(\texttt{localArea}, i)$; and
- the values strictly decrease over the `localArea` positions **after** $i$:
  $\texttt{rawData}[i] > \texttt{rawData}[i+1] > \dots > \texttt{rawData}[i+m']$,
  where $m' = \min(\texttt{localArea}, n - 1 - i)$.

Near the ends of the signal, only the neighbours that exist are checked. With
`localArea = 0` every index qualifies. Return the indices in increasing order.

Both $n$ and `localArea` can reach $10^5$, so checking every neighbour of
every index is too slow.

## Constraints

- `1 <= n <= 10⁵`; `-10⁹ <= rawData[i] <= 10⁹`
- `0 <= localArea <= 10⁵`

## Examples

**Example 1**
```
Input:  rawData = [1, 3, 5, 4, 2, 6, 1], localArea = 2
Output: [2]
Explanation: 1 < 3 < 5 and 5 > 4 > 2. Index 5 (value 6) is above both its
neighbours, but the two values before it, 4 and 2, are not increasing.
```

**Example 2**
```
Input:  rawData = [5, 4, 3, 4, 5], localArea = 3
Output: []
Explanation: index 0 has no left neighbours, but its 3 right neighbours
4, 3, 4 do not keep falling; index 4 fails in the same way on its left.
```

**Example 3**
```
Input:  rawData = [2, 4, 4, 1, 3], localArea = 1
Output: [4]
Explanation: the two 4s are not strictly above each other. Index 4 has a
single neighbour, 1, which is smaller.
```
