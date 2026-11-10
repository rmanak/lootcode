When the storage fills up, users want to find out which files take up the most
space, so implement an operation that lists the largest files whose names
start with a given prefix — for example, everything under one folder.

```python
get_n_largest(self, prefix: str, n: int) -> list[str]
```

should return the `n` largest files whose names start with `prefix`, in the
following format:

```
["<name_1>(<size_1>)", "<name_2>(<size_2>)", ..., "<name_n>(<size_n>)"]
```

Additional conditions:

- Files are sorted in descending order of size or, in the case of ties, in
  lexicographical order of their names.
- If fewer than `n` files match, return all of them. If no file matches, or
  `n` is `0`, return an empty list.
- The empty prefix matches every file, and a prefix equal to a whole file name
  matches that file. Matching is case-sensitive.
- "Lexicographical order" means ordinary Python string comparison (`<` on
  `str`): uppercase letters sort before lowercase ones, and digits are compared
  character by character (`"f10"` before `"f9"`).

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage |
| `storage.add_file("/dir/file1.txt", 5)` | returns `True` |
| `storage.add_file("/dir/file2", 20)` | returns `True` |
| `storage.add_file("/dir/deeper/file3.mov", 9)` | returns `True` |
| `storage.add_file("/other/file4.txt", 20)` | returns `True` |
| `storage.get_n_largest("/dir", 2)` | returns `["/dir/file2(20)", "/dir/deeper/file3.mov(9)"]`; `"/other/file4.txt"` does not start with `"/dir"` |
| `storage.get_n_largest("/dir", 10)` | returns `["/dir/file2(20)", "/dir/deeper/file3.mov(9)", "/dir/file1.txt(5)"]`; only three files match |
| `storage.get_n_largest("", 2)` | returns `["/dir/file2(20)", "/other/file4.txt(20)"]`; two files of size 20 are ordered by name |
| `storage.get_n_largest("/dir/file", 0)` | returns `[]` |
| `storage.get_n_largest("/tmp", 3)` | returns `[]`; no file starts with `"/tmp"` |
