Schedule jobs (which must be done in order) over `d` days, at least one job per day.
A day's difficulty is the maximum difficulty among its jobs; the schedule's difficulty
is the sum over days. **Return the minimum possible schedule difficulty, or `-1` if it
is impossible.**

**Examples**
```
jobDifficulty = [6,5,4,3,2,1], d = 2  ->  7
jobDifficulty = [9,9,9], d = 4        ->  -1
jobDifficulty = [1,1,1], d = 3        ->  3
```

**Constraints:** `1 <= len(jobDifficulty) <= 300`, `0 <= jobDifficulty[i] <= 1000`,
`1 <= d <= 10`.
