`citations` is sorted ascending; `citations[i]` is the citation count of a paper.
The **h-index** is the largest `h` such that `h` papers have at least `h` citations
each. **Return the h-index.** Aim for `O(log n)`.

**Example**
```
citations = [0,1,3,5,6]  ->  3
```

**Constraints:** `0 <= len(citations) <= 10^5`, sorted ascending,
`0 <= citations[i] <= 1000`.
