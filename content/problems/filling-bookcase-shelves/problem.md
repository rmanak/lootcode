`books[i] = [thickness, height]`. Place the books, **in the given order**, onto
shelves each of width `shelfWidth`. Fill a shelf with a prefix of the remaining
books whose total thickness is at most `shelfWidth`, then start a new shelf above it;
that shelf adds the maximum height of the books on it to the total height. Return the
minimum possible total height of the bookcase.

**Example**
```
books = [[1,1],[2,3],[2,3],[1,1],[1,1],[1,1],[1,2]], shelfWidth = 4   ->  6
```

**Constraints:** `1 <= len(books) <= 1000`,
`1 <= books[i][0] <= shelfWidth <= 1000`, `1 <= books[i][1] <= 1000`.
