Initially, the cloud storage system does not contain any files, so implement
operations to add new files, copy an existing file to a new name, and look up
how much space a file takes.

```python
add_file(self, name: str, size: int) -> bool
```

should add a new file `name` to the storage. `size` is the amount of memory the
file requires, in bytes. Returns `True` if the file was added successfully, or
`False` if a file with the same name already exists — in which case the
existing file is left exactly as it was.

```python
copy_file(self, name_from: str, name_to: str) -> bool
```

should copy the file at `name_from` to a new file `name_to` of the same size.
The original file stays where it is, and from then on the two files are
independent. The directories in `name_to` do not need to contain any files
already. Returns `True` if the file was copied successfully, or `False`
otherwise, in which case nothing changes. Specifically:

- Returns `False` if `name_from` points to a file that doesn't exist.
- Returns `False` if `name_from` points to a directory rather than a file —
  for example `"/dir1"` while the file `"/dir1/file.txt"` exists.
- Returns `False` if a file named `name_to` already exists, which includes
  copying a file onto itself.

```python
get_file_size(self, name: str) -> int | None
```

should return the size of the file `name` in bytes if it exists, or `None`
otherwise. A directory is not a file, so a directory name returns `None` as
well.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage |
| `storage.add_file("/dir1/dir2/file.txt", 10)` | returns `True`; adds the file `"/dir1/dir2/file.txt"` of 10 bytes; storage: `{"/dir1/dir2/file.txt": 10}` |
| `storage.copy_file("/not-existing.file", "/dir1/file.txt")` | returns `False`; the file `"/not-existing.file"` doesn't exist |
| `storage.copy_file("/dir1/dir2/file.txt", "/dir1/file.txt")` | returns `True`; adds the file `"/dir1/file.txt"`; storage: `{"/dir1/dir2/file.txt": 10, "/dir1/file.txt": 10}` |
| `storage.add_file("/dir1/file.txt", 15)` | returns `False`; the file `"/dir1/file.txt"` already exists |
| `storage.copy_file("/dir1/file.txt", "/dir1/dir2/file.txt")` | returns `False`; the file `"/dir1/dir2/file.txt"` already exists |
| `storage.copy_file("/dir1/dir2", "/backup")` | returns `False`; `"/dir1/dir2"` is a directory, not a file |
| `storage.get_file_size("/dir1/file.txt")` | returns `10` |
| `storage.get_file_size("/not-existing.file")` | returns `None` |
