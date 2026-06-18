Given an array `temperatures`, return **an array `answer` where `answer[i]` is the
number of days you must wait after day `i` to get a warmer temperature**. If no
warmer day exists, `answer[i] = 0`.

## Constraints
- `1 <= len(temperatures) <= 10^5`.
- `-50 <= temperatures[i] <= 150`.

## Examples
Input: `temperatures = [73,74,75,71,69,72,76,73]`
Output: `[1,1,4,2,1,1,0,0]`

Input: `temperatures = [30,40,50,60]`
Output: `[1,1,1,0]`

Input: `temperatures = [30,30,30]`
Output: `[0,0,0]`
