As the storage fills up, people need to find their files again. Implement
support for retrieving files by searching for names that start with a given
prefix and end with a given suffix — for example, every file in one directory,
or every file of one type wherever it is kept.

```python
find_file(self, prefix: str, suffix: str) -> list[str]
```

should search for files with names starting with `prefix` and ending with
`suffix`. Returns a list of strings representing all matching files in the
following format:

```
["<name_1>(<size_1>)", "<name_2>(<size_2>)", ..., "<name_n>(<size_n>)"]
```

The output should be sorted in descending order of file sizes or, in the case
of ties, in ascending lexicographic order of file names. If no files match the
required properties, returns an empty list.

Additional conditions:

- The prefix and the suffix are checked independently, and they may overlap:
  the name `"/ab"` starts with `"/a"` and ends with `"ab"`, so it matches both.
- An empty prefix or suffix matches every name on that side; with both empty,
  every file matches.
- Matching uses plain string operations and is case-sensitive. The prefix does
  not have to end at a directory boundary, so the prefix `"/dir"` matches
  `"/dir/a.txt"` and also `"/dir2/b.txt"`.
- "Lexicographic" means ordinary string comparison: uppercase letters come
  before lowercase ones, and `"/f10"` comes before `"/f9"`.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage |
| `storage.add_file("/dir/file1.txt", 5)` | returns `True` |
| `storage.add_file("/dir/file2.txt", 20)` | returns `True` |
| `storage.add_file("/dir/deeper/file3.mov", 9)` | returns `True` |
| `storage.copy_file("/dir/file1.txt", "/dir/deeper/file1.txt")` | returns `True` |
| `storage.add_file("/dir2/file4.txt", 20)` | returns `True`; storage: `{"/dir/file1.txt": 5, "/dir/file2.txt": 20, "/dir/deeper/file3.mov": 9, "/dir/deeper/file1.txt": 5, "/dir2/file4.txt": 20}` |
| `storage.find_file("/dir/", ".txt")` | returns `["/dir/file2.txt(20)", "/dir/deeper/file1.txt(5)", "/dir/file1.txt(5)"]`; the two files of 5 bytes are ordered by name |
| `storage.find_file("/dir", ".txt")` | returns `["/dir/file2.txt(20)", "/dir2/file4.txt(20)", "/dir/deeper/file1.txt(5)", "/dir/file1.txt(5)"]`; the prefix `"/dir"` also matches `"/dir2/file4.txt"`, and `"/dir/file2.txt"` comes first because `"/"` sorts before `"2"` |
| `storage.find_file("/dir/deeper/", "")` | returns `["/dir/deeper/file3.mov(9)", "/dir/deeper/file1.txt(5)"]`; the empty suffix matches every name |
| `storage.find_file("/dir", ".mp3")` | returns `[]`; no name ends with `".mp3"` |
| `storage.find_file("/deeper", ".mov")` | returns `[]`; names must *start* with the prefix |
| `storage.find_file("/dir/file2.txt", "file2.txt")` | returns `["/dir/file2.txt(20)"]`; the prefix and the suffix may overlap |
