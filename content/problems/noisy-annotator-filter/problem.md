A classifier's training labels come from several human annotators, and some
of them are careless. A simple, standard way to find them is to measure how
often each annotator agrees with the **other** annotators on the same items,
drop the ones who agree too rarely, and re-derive the labels from the rest.

`annotations[i][a]` is the label annotator $a$ gave item $i$ (a non-negative
integer), or $-1$ if $a$ did not label item $i$.

1. **Agreement.** For each annotator $a$ and each item $i$ that $a$ labeled,
   take the **majority label of the other annotators** on item $i$ (the most
   common label among their labels; on a tie, the smallest label). Skip the
   item if nobody else labeled it. Annotator $a$'s agreement rate is the
   fraction of the non-skipped items on which $a$'s label equals that majority.
   If every item was skipped, the rate is undefined: report it as $-1$.
2. **Filter.** Annotator $a$ is **bad** if its rate is defined and strictly
   below `threshold`.
3. **Relabel.** Each item's clean label is the majority label (ties to the
   smallest) among the annotators who are **not** bad, or $-1$ if none of them
   labeled it.

Leaving the annotator out of its own reference matters: with three annotators
per item, a careless one would otherwise agree with "the majority" every time
it is part of a 1–1–1 tie that it wins.

**Return `[rates, bad, labels]`**: the agreement rate of every annotator (in
order), the indices of the bad annotators in increasing order, and the clean
label of every item.

## Constraints

- `1 <= N <= 2000` items and `1 <= A <= 50` annotators; every row has `A` entries
- Every entry is `-1` or a label in `[0, 100]`
- `0 <= threshold <= 1`

## Examples

**Example 1**
```
Input:  annotations = [[1, 1, 0], [0, 0, 1], [2, 2, 2], [1, 1, 2]], threshold = 0.5
Output: [[0.75, 0.75, 0.25], [2], [1, 0, 2, 1]]
Explanation: annotator 0 is compared with the majority of annotators 1 and 2
on each item. On item 0 that is the tie {1, 0}, whose majority is 0, so
annotator 0's label 1 disagrees; it agrees on the other three items. Annotator
2 agrees only on item 2 (rate 0.25 < 0.5) and is dropped; items 0, 1 and 3
are then relabelled by annotators 0 and 1 alone.
```

**Example 2**
```
Input:  annotations = [[0, 1, 2], [3, 3, -1], [-1, 5, 5], [4, -1, -1]], threshold = 0.5
Output: [[0.5, 0.6666666666666666, 0.5], [], [0, 3, 5, 4]]
Explanation: on item 0 every annotator sees a 1-1 tie among the other two,
and the smaller label wins: annotator 0 (label 0) faces {1, 2} and
disagrees. Item 3 has a single annotator and is skipped. A rate equal to the
threshold is not bad.
```

**Example 3**
```
Input:  annotations = [[2, 0, 2, -1], [1, 1, 1, 1], [-1, -1, 1, 2], [2, 2, 0, 2], [-1, 1, 1, 1]], threshold = 0.6
Output: [[0.6666666666666666, 0.75, 0.4, 0.75], [2], [0, 1, 2, 2, 1]]
Explanation: annotator 2 agrees on 2 of its 5 items and is dropped. Without
it, item 0 holds only the labels 2 and 0, a tie that goes to 0, and item 2
holds only annotator 3's label 2.
```
