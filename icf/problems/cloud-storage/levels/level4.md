Space in the cloud is limited, so users should be able to **compress** the
files they do not need right away. Compressing a file replaces it with a
compressed version that takes up half as much of its owner's capacity, and
decompressing brings the original back. Implement support for file compression.

```python
compress_file(self, user_id: str, name: str) -> int | None
```

should compress the file `name` if it belongs to `user_id`. The compressed file
is replaced with a new file named `<name>.COMPRESSED` — the original name
followed by the suffix `".COMPRESSED"`. The size of the newly created file is
equal to half the size of the original file, and it is owned by `user_id`, the
owner of the original file. It is guaranteed that a file being compressed has an
even size, so there are no fractional calculations, and that `name` never points
to a compressed file — that is, it never ends with `".COMPRESSED"`. Returns the
remaining storage capacity for `user_id` if the file was compressed
successfully, or `None` otherwise. Specifically:

- Returns `None` if `user_id` doesn't exist.
- Returns `None` if the file `name` doesn't exist, or is not owned by `user_id`.
- Returns `None` if a file named `<name>.COMPRESSED` already exists.

```python
decompress_file(self, user_id: str, name: str) -> int | None
```

should revert the compression of the file `name` if it belongs to `user_id`.
Here `name` is the name of the compressed file, suffix included — such as
`"/dir/file.mp4.COMPRESSED"`. The compressed file is removed, and the original
file is added back under the name without the suffix, with twice the compressed
size and the same owner. Returns the remaining storage capacity for `user_id` if
the file was decompressed successfully, or `None` otherwise. Specifically:

- Returns `None` if `user_id` doesn't exist.
- Returns `None` if the file `name` doesn't exist, or is not owned by `user_id`.
- Returns `None` if `name` doesn't end with `".COMPRESSED"`: only a compressed
  file can be decompressed.
- Returns `None` if a decompressed version of the file already exists — a file
  with `name` minus the suffix.
- Returns `None` if decompression would make `user_id`'s total exceed their
  storage capacity. Filling the capacity exactly is allowed.

### Additional conditions

- A compressed file is an ordinary file in every other respect: `get_file_size`,
  `find_file`, `copy_file` and `update_capacity` all see it with its compressed
  size.
- Compressed files cannot be added directly: `add_file` and `add_file_by` are
  never called with a name that ends with `".COMPRESSED"`.
- It is guaranteed that all `copy_file` operations preserve the suffix
  `".COMPRESSED"`: `name_to` ends with it exactly when `name_from` does. The
  copy of a compressed file is therefore a compressed file too, and can be
  decompressed under its own name.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage with no users |
| `storage.add_user("user1", 1000)` | returns `True` |
| `storage.add_user("user2", 5000)` | returns `True` |
| `storage.add_file_by("user1", "/dir/file.mp4", 500)` | returns `500` |
| `storage.compress_file("user2", "/dir/file.mp4")` | returns `None`; the file `"/dir/file.mp4"` is owned by `"user1"` |
| `storage.compress_file("user3", "/dir/file.mp4")` | returns `None`; `"user3"` doesn't exist |
| `storage.compress_file("user1", "/folder/non_existing_file")` | returns `None`; the file `"/folder/non_existing_file"` doesn't exist |
| `storage.compress_file("user1", "/dir/file.mp4")` | returns `750`; the file `"/dir/file.mp4"` is compressed to size 500 / 2 = 250 bytes; storage: `{"/dir/file.mp4.COMPRESSED": 250}` |
| `storage.get_file_size("/dir/file.mp4.COMPRESSED")` | returns `250` |
| `storage.get_file_size("/dir/file.mp4")` | returns `None`; the file was replaced by its compressed version |
| `storage.copy_file("/dir/file.mp4.COMPRESSED", "/file.mp4.COMPRESSED")` | returns `True`; the copy is owned by `"user1"`, who now uses 500 bytes |
| `storage.add_file_by("user1", "/dir/file.mp4", 500)` | returns `0`; the name `"/dir/file.mp4"` is free while that file is compressed |
| `storage.find_file("/dir/", "")` | returns `["/dir/file.mp4(500)", "/dir/file.mp4.COMPRESSED(250)"]` |
| `storage.decompress_file("user1", "/file.mp4.COMPRESSED")` | returns `None`; decompressing would add 250 bytes, but `"user1"` has no capacity left |
| `storage.update_capacity("user1", 2000)` | returns `0` |
| `storage.decompress_file("user2", "/dir/file.mp4.COMPRESSED")` | returns `None`; the file `"/dir/file.mp4.COMPRESSED"` is owned by `"user1"` |
| `storage.decompress_file("user1", "/dir/file.mp4.COMPRESSED")` | returns `None`; the file `"/dir/file.mp4"` exists already |
| `storage.decompress_file("user1", "/dir/file.mp4")` | returns `None`; `"/dir/file.mp4"` is not a compressed file |
| `storage.decompress_file("user1", "/file.mp4.COMPRESSED")` | returns `750`; `"user1"` now owns 500 + 250 + 500 = 1250 bytes; storage: `{"/dir/file.mp4.COMPRESSED": 250, "/dir/file.mp4": 500, "/file.mp4": 500}` |
| `storage.get_file_size("/file.mp4")` | returns `500` |
