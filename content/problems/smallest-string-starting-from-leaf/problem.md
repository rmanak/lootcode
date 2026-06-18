A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and is rebuilt inside your function. Each node's value is `0..25`,
representing `'a'..'z'`.

Consider every path that starts at a leaf and ends at the root, reading the
corresponding letters. Return the lexicographically smallest such string. (Recall a
shorter string that is a prefix of another is the smaller one, e.g. `"ab" < "aba"`.)

**Examples**
```
root = [0,1,2,3,4,3,4]            ->  "dba"
root = [25,1,3,1,3,0,2]           ->  "adz"
root = [2,2,1,null,1,0,null,0]    ->  "abc"
```

**Constraints:** `1 <= number of nodes <= 8500`, each value is `0..25`.
