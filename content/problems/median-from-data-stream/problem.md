The **median** is the middle value in an ordered integer list. If the size of the
list is even, there is no middle value, and the median is the mean of the two
middle values.

- For `arr = [2,3,4]`, the median is `3`.
- For `arr = [2,3]`, the median is `(2 + 3) / 2 = 2.5`.

Implement the `MedianFinder` class:

- `MedianFinder()` initializes the `MedianFinder` object.
- `void addNum(int num)` adds the integer `num` from the data stream to the
  structure.
- `double findMedian()` returns the median of all elements added so far. Return it
  as a float (so `2` is `2.0`).

**Example 1:**

```
Input
["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]
[[], [1], [2], [], [3], []]

Output
[null, null, null, 1.5, null, 2.0]
```

Explanation: after `1` and `2`, the median is `(1 + 2) / 2 = 1.5`; after `3` is
added, the median is `2.0`.

**Example 2:**

```
Input
["MedianFinder", "addNum", "findMedian"]
[[], [5], []]

Output
[null, null, 5.0]
```

**Constraints:**

- `-10⁶ <= num <= 10⁶`
- `findMedian` is only called after at least one `addNum` call.
- At most `10⁵` calls will be made to `addNum` and `findMedian`.
