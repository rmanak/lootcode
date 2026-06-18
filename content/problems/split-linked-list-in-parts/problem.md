A singly linked list is given as an array of values `root`. Split it into `k`
consecutive parts whose sizes differ by at most one, with earlier parts being at least
as large as later parts. Some parts may be empty. Return the list of parts (each as an
array of values; an empty part is `[]`).

**Examples**
```
root = [1,2,3], k = 5                     ->  [[1],[2],[3],[],[]]
root = [1,2,3,4,5,6,7,8,9,10], k = 3      ->  [[1,2,3,4],[5,6,7],[8,9,10]]
```

**Constraints:** `0 <= len(root) <= 1000`, `1 <= k <= 50`.
