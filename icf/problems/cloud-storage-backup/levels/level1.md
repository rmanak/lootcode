The cloud storage system starts out empty, so implement the basic file
operations: adding a file, reading its size, deleting it, and copying it under
a new name.

```python
add_file(self, name: str, size: int) -> bool
```

should add a new file `name` to the storage, with a size of `size` bytes.
Returns `True` if the file was added, or `False` if a file with the same name
already exists — in which case the existing file is left exactly as it was.

```python
get_file_size(self, name: str) -> int | None
```

should return the size of the file `name`, or `None` if it doesn't exist.

```python
delete_file(self, name: str) -> int | None
```

should delete the file `name`. Returns the size of the deleted file, or `None`
if it doesn't exist. Once a file is deleted, its name is free to be used again.

```python
copy_file(self, name_from: str, name_to: str) -> bool
```

should copy the file at `name_from` to a new file `name_to`, with the same
size. Returns `True` if the file was copied, or `False` otherwise, in which
case nothing changes. Specifically:

- Returns `False` if no file `name_from` exists.
- Returns `False` if a file `name_to` already exists — including when
  `name_to` is the same as `name_from`.

The copy is a file of its own: deleting either one leaves the other in place.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage |
| `storage.add_file("/dir1/dir2/file.txt", 10)` | returns `True` |
| `storage.add_file("/dir1/dir2/file.txt", 5)` | returns `False`; the name is already taken, so nothing changes |
| `storage.copy_file("/dir1/dir2/file.txt", "/dir1/file.txt")` | returns `True` |
| `storage.get_file_size("/dir1/file.txt")` | returns `10`; the copy has the size of the original |
| `storage.copy_file("/not-there.txt", "/x.txt")` | returns `False`; there is no file `"/not-there.txt"` |
| `storage.copy_file("/dir1/file.txt", "/dir1/dir2/file.txt")` | returns `False`; the destination already exists |
| `storage.delete_file("/dir1/dir2/file.txt")` | returns `10`; the size of the deleted file |
| `storage.get_file_size("/dir1/dir2/file.txt")` | returns `None`; the file is gone |
| `storage.get_file_size("/dir1/file.txt")` | returns `10`; deleting the original does not touch the copy |
| `storage.delete_file("/dir1/dir2/file.txt")` | returns `None`; already deleted |
