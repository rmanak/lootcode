Given an array of `words` and a width `maxWidth`, format the text so every line is
exactly `maxWidth` characters and fully justified. Pack greedily; distribute extra
spaces between words as evenly as possible, with the **left** gaps receiving more
spaces when they do not divide evenly. The **last** line is left-justified (single
spaces between words, padded with trailing spaces). A line with one word is also left-
justified.

**Example**
```
words = ["This","is","an","example","of","text","justification."], maxWidth = 16
->  ["This    is    an","example  of text","justification.  "]
```

**Constraints:** `1 <= len(words)`, each word length `<= maxWidth`, `1 <= maxWidth`.
