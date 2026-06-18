A word is **valid** with respect to a puzzle string if (1) the word contains the
puzzle's **first** letter, and (2) every letter of the word appears in the puzzle.
For each puzzle, count how many words in `words` are valid for it. Return `answer`,
where `answer[i]` is the count for `puzzles[i]`.

**Example**
```
words   = ["aaaa","asas","able","ability","actt","actor","access"]
puzzles = ["aboveyz","abrodyz","abslute","absoryz","actresz","gaswxyz"]
   ->  [1,1,3,2,4,0]
```

**Constraints:** `1 <= len(words) <= 10^5`, `4 <= len(words[i]) <= 50`,
`1 <= len(puzzles) <= 10^4`, `len(puzzles[i]) == 7` with distinct letters; lowercase.
