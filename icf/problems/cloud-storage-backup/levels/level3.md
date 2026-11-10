Implement support for different users. All users share the one filesystem, but
each user owns the files it adds and is given an individual **storage
capacity**: the most bytes its files may take up in total. Two users can also
combine their accounts — for example, when a team consolidates its storage.

```python
add_user(self, user_id: str, capacity: int) -> bool
```

should add a new user with a storage capacity of `capacity` bytes. Returns
`True` if the user was created, or `False` if a user with `user_id` already
exists — in which case that user's capacity does not change.

```python
add_file_by(self, user_id: str, name: str, size: int) -> int | None
```

should behave in the same way as `add_file` from level 1, but the new file is
owned by `user_id`. Returns the user's **remaining capacity** after the file
was added — its capacity minus the total size of the files it owns — or `None`
otherwise, in which case nothing changes. Specifically:

- Returns `None` if `user_id` doesn't exist.
- Returns `None` if a file named `name` already exists.
- Returns `None` if the new file would make the user's total exceed its
  capacity. Filling the capacity exactly is allowed, and leaves `0`.

```python
merge_user(self, user_id_1: str, user_id_2: str) -> int | None
```

should merge the account of `user_id_2` into the account of `user_id_1`.
Returns the remaining capacity of `user_id_1` after the merge, or `None` if the
merge is refused, in which case nothing changes. Specifically:

- Returns `None` if `user_id_1` is equal to `user_id_2`.
- Returns `None` if either user doesn't exist, or either one is the
  administrator (see below).
- The capacity of `user_id_2` is added to the capacity of `user_id_1`.
- Every file owned by `user_id_2` now belongs to `user_id_1`; the files keep
  their names and sizes.
- `user_id_2` is removed from the system. Its identifier becomes free:
  `add_user` can later create a brand-new user with that identifier, which owns
  nothing.

### The administrator

The system always contains one special user, `"admin"`, with **unlimited**
capacity. It exists from the start, so `add_user("admin", ...)` returns
`False`.

- Every file added with `add_file` — at this level and before — is owned by
  the administrator.
- The administrator is not a regular user: `add_file_by("admin", ...)` returns
  `None`, and `merge_user` refuses to involve it.

### How the existing operations change

- `copy_file`: the copy is owned by the **owner of the original file** and
  counts against that owner's capacity. If the copy would make the owner's
  total exceed its capacity, `copy_file` returns `False` and nothing changes.
  Copies of the administrator's files always fit.
- `delete_file`: deleting a file frees its size from its owner's capacity.
- `get_n_largest` lists matching files of every owner.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage |
| `storage.add_user("user1", 200)` | returns `True` |
| `storage.add_user("user1", 100)` | returns `False`; the user already exists |
| `storage.add_user("user2", 100)` | returns `True` |
| `storage.add_file_by("user1", "/dir/file.med", 50)` | returns `150`; user1 has 200 - 50 = 150 left |
| `storage.add_file_by("user1", "/file.big", 140)` | returns `10` |
| `storage.copy_file("/file.big", "/dir/file.big")` | returns `False`; the copy would belong to user1, who has only 10 left |
| `storage.add_file_by("user2", "/dir/file.small", 30)` | returns `70` |
| `storage.add_file("/dir/admin.cfg", 1000)` | returns `True`; owned by the administrator, who has no limit |
| `storage.merge_user("user1", "user1")` | returns `None`; a user cannot be merged with itself |
| `storage.merge_user("user1", "admin")` | returns `None`; the administrator cannot be merged |
| `storage.merge_user("user1", "user2")` | returns `80`; capacity 200 + 100 = 300, used 50 + 140 + 30 = 220 |
| `storage.add_file_by("user2", "/new.txt", 1)` | returns `None`; user2 no longer exists |
| `storage.copy_file("/dir/file.small", "/file.small")` | returns `True`; the file came from user2 and now belongs to user1, so the copy is user1's too; 80 - 30 = 50 left |
| `storage.add_file_by("user1", "/x", 51)` | returns `None`; only 50 left |
