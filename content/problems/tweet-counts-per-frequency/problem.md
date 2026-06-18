A tweet was recorded at each second in `times`. Given a bucket size `freq`
(`"minute"` = 60s, `"hour"` = 3600s, `"day"` = 86400s) and a window
`[startTime, endTime]`, split the window into consecutive intervals
`[startTime + d*i, startTime + d*(i+1))` (where `d` is the bucket size in seconds),
clipping the final interval at `endTime + 1`. Return the number of recorded times
that fall in each interval, in order.

**Examples**
```
freq="minute", times=[0,60,10], startTime=0, endTime=59   ->  [2]
freq="minute", times=[0,60,10], startTime=0, endTime=60   ->  [2,1]
freq="hour",   times=[0,10,60,120], startTime=0, endTime=210  ->  [4]
```

**Constraints:** `0 <= times[i], startTime, endTime <= 10^9`,
`0 <= endTime - startTime <= 10^4`.
