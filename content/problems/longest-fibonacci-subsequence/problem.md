Given a **strictly increasing** array `arr`, return the length of the longest
Fibonacci-like subsequence (length `>= 3` where each element equals the sum of the
previous two). Return `0` if none exists.

## Constraints
- `3 <= len(arr) <= 1000`
- `1 <= arr[i] < arr[i+1] <= 10^9`

## Examples
Input: `arr = [1,2,3,4,5,6,7,8]`
Output: `5`
Explanation: `[1,2,3,5,8]` is Fibonacci-like.

Input: `arr = [1,3,7,11,12,14,18]`
Output: `3`
Explanation: e.g. `[1,11,12]` or `[3,11,14]`.
