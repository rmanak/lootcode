Replay a stream of `operations` and return **the list of results**. Each operation
is `["addNum", x]` (returns `null`) or `["findMedian"]` (returns the median of all
numbers added so far, as a float — the average of the two middle values when the
count is even).

## Constraints
- `1 <= len(operations) <= 10^5`; a `findMedian` is only issued after at least one
  `addNum`.
- `-10^6 <= x <= 10^6`.

## Examples
Input: `operations = [["addNum",1],["addNum",2],["findMedian"],["addNum",3],["findMedian"]]`
Output: `[null,null,1.5,null,2.0]`

Input: `operations = [["addNum",5],["findMedian"]]`
Output: `[null,5.0]`

Input: `operations = [["addNum",2],["addNum",4],["findMedian"]]`
Output: `[null,null,3.0]`
