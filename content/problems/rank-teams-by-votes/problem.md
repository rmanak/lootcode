Each voter ranks all teams from highest to lowest. Teams are ordered by the number
of first-place votes; ties are broken by second-place votes, then third, and so on.
If still tied after every position, order them **alphabetically** by team letter.
**Return the teams as a single string in final ranked order.**

**Examples**
```
votes = ["ABC","ACB","ABC","ACB","ACB"]  ->  "ACB"
votes = ["WXYZ","XYZW"]                   ->  "XWYZ"
votes = ["BCA","CAB","CBA","ABC","ACB","BAC"]  ->  "ABC"
```

**Constraints:** `1 <= len(votes) <= 1000`, all votes are permutations of the same
upper-case letters.
