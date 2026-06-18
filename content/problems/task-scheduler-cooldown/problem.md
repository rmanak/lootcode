Given a list of `tasks` (each a single uppercase letter) and a cooldown `n`, each
task takes one unit of time and two runs of the **same** task must be separated by
at least `n` idle/other units. Return **the minimum number of time units** needed
to finish all tasks.

## Constraints
- `1 <= len(tasks) <= 10^4`, each task is `A`–`Z`.
- `0 <= n <= 100`.

## Examples
Input: `tasks = ["A","A","A","B","B","B"], n = 2`
Output: `8`
Explanation: `A B idle A B idle A B`.

Input: `tasks = ["A","A","A","B","B","B"], n = 0`
Output: `6`

Input: `tasks = ["A","B","C","D"], n = 2`
Output: `4`
