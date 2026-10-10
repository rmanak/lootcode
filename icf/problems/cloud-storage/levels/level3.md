Implement support for different users sending queries to the system. All users
share a common filesystem in the cloud storage, but each user owns the files
they add and is assigned an individual **storage capacity**: the most bytes
their files may take up in total.

```python
add_user(self, user_id: str, capacity: int) -> bool
```

should add a new user to the system, with `capacity` as their storage limit in
bytes. The total size of all files owned by `user_id` may never exceed
`capacity`. Returns `True` if a user with `user_id` is successfully created, or
`False` if a user with `user_id` already exists — in which case that user's
capacity does not change.

```python
add_file_by(self, user_id: str, name: str, size: int) -> int | None
```

should behave in the same way as `add_file` from level 1, but the added file is
owned by the user with `user_id`. Returns the **remaining storage capacity** for
`user_id` after the file was added — their capacity minus the total size of
all the files they own — or `None` otherwise. Specifically:

- Returns `None` if `user_id` doesn't exist.
- Returns `None` if a file named `name` already exists.
- Returns `None` if adding the file would make the user's total exceed their
  capacity. Filling the capacity exactly is allowed, and leaves `0`.

```python
update_capacity(self, user_id: str, capacity: int) -> int | None
```

should change the maximum storage capacity for the user with `user_id`. If the
total size of all the user's files exceeds the new capacity, the user's files
are removed from the storage one at a time — **the largest file first**, and
among files of the same size, the one whose name comes first lexicographically —
until the total size of the remaining files no longer exceeds the new capacity.
The removal stops at that moment, even if removing a smaller file instead would
also have been enough. Removed files are gone for good, and their names are free
to use again. Returns the number of removed files (`0` if everything fits), or
`None` if a user with `user_id` doesn't exist. The new capacity applies to every
later operation, whether it is larger or smaller than the old one.

### How the existing operations change

- All queries calling `add_file` from level 1 are run by the user with
  `user_id = "admin"`, who has **unlimited** storage capacity: the files it adds
  never count against any limit and are never removed by `update_capacity`.
  `"admin"` is never passed as the `user_id` of any operation.
- `copy_file` preserves the ownership of the original file: the copy is owned by
  the same user, and it takes up as much of that user's capacity as the
  original. `copy_file` returns `False` if the copy would make the owner's total
  exceed their capacity. A copy of a file owned by `"admin"` always fits.
- `get_file_size` and `find_file` see every file, whoever owns it.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage with no users |
| `storage.add_user("user1", 200)` | returns `True`; creates `"user1"` with a capacity of 200 bytes |
| `storage.add_user("user1", 100)` | returns `False`; `"user1"` already exists, and its capacity stays 200 |
| `storage.add_user("user2", 100)` | returns `True` |
| `storage.add_file_by("user1", "/dir/file.big", 100)` | returns `100`; 200 - 100 |
| `storage.add_file_by("user1", "/file.med", 30)` | returns `70` |
| `storage.add_file_by("user2", "/file.med", 40)` | returns `None`; the file `"/file.med"` already exists |
| `storage.add_file_by("user3", "/file.small", 10)` | returns `None`; `"user3"` doesn't exist |
| `storage.copy_file("/file.med", "/dir/another/file.med")` | returns `True`; the copy is owned by `"user1"`, who now has 40 bytes left |
| `storage.add_file_by("user1", "/dir/file.small", 50)` | returns `None`; `"user1"` does not have enough capacity left |
| `storage.add_file_by("user1", "/dir/file.small", 40)` | returns `0`; the file fills the capacity exactly |
| `storage.add_file("/dir/admin_file", 300)` | returns `True`; owned by `"admin"`, who has unlimited capacity |
| `storage.update_capacity("user1", 300)` | returns `0`; all of `"user1"`'s files fit |
| `storage.update_capacity("user1", 50)` | returns `3`; `"user1"` owns 200 bytes, so `"/dir/file.big"` (100) is removed first, then `"/dir/file.small"` (40), then `"/dir/another/file.med"` (30, whose name comes before `"/file.med"`), leaving 30 |
| `storage.get_file_size("/file.med")` | returns `30` |
| `storage.get_file_size("/dir/another/file.med")` | returns `None`; the file was removed |
| `storage.get_file_size("/dir/admin_file")` | returns `300`; files added with `add_file` are never removed |
| `storage.update_capacity("user3", 100)` | returns `None`; `"user3"` doesn't exist |
| `storage.add_file_by("user1", "/dir/file.big", 20)` | returns `0`; the removed file's name is free again, and 30 + 20 fills the new capacity of 50 |
