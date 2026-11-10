Users want to protect themselves against mistakes, so implement operations to
back up the files a user owns and to restore them later — bringing back what
was deleted and getting rid of what was added since.

```python
backup_user(self, user_id: str) -> int | None
```

should save a backup of the files currently owned by `user_id`: the name and
the size of each one. Returns the number of files in the backup, or `None` if
`user_id` doesn't exist or is the administrator. A user keeps only its most
recent backup — a new call replaces the previous one. A user with no files can
still be backed up; its backup is empty.

```python
restore_user(self, user_id: str) -> int | None
```

should restore the files of `user_id` to the state of its latest backup.
Returns the number of files that were restored, or `None` if `user_id` doesn't
exist or is the administrator. Specifically:

1. First, every file `user_id` currently owns is deleted, including the files
   that are also in the backup.
2. Then, each file in the backup is re-created with its backed-up size, owned
   by `user_id`, in lexicographical order of the file names.
3. A file whose name is now taken by a file of **another** owner is skipped:
   that file is left alone, and the skipped file does not count in the result.

If the user has never made a backup, all of its files are deleted and `0` is
returned. Restoring does not use the backup up: the same backup can be
restored again later. Restored files always fit, because a user's capacity
never shrinks.

How the existing operations change:

- `merge_user` discards the backup of `user_id_2`; the backup of `user_id_1`
  is unchanged and still lists only the files `user_id_1` owned when it was
  taken. A user re-created under a merged-away identifier has no backup.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `storage = CloudStorage()` | an empty storage |
| `storage.add_user("user1", 100)` | returns `True` |
| `storage.add_file_by("user1", "/a.txt", 10)` | returns `90` |
| `storage.add_file_by("user1", "/b.txt", 20)` | returns `70` |
| `storage.backup_user("user1")` | returns `2`; the backup holds `"/a.txt"` and `"/b.txt"` |
| `storage.delete_file("/a.txt")` | returns `10` |
| `storage.add_file_by("user1", "/c.txt", 30)` | returns `50` |
| `storage.add_file("/a.txt", 99)` | returns `True`; the administrator takes the free name |
| `storage.restore_user("user1")` | returns `1`; `"/c.txt"` is deleted because it is not in the backup, `"/b.txt"` is re-created, and `"/a.txt"` is skipped because the administrator owns that name now |
| `storage.get_file_size("/a.txt")` | returns `99`; the administrator's file is untouched |
| `storage.get_file_size("/c.txt")` | returns `None` |
| `storage.delete_file("/a.txt")` | returns `99` |
| `storage.restore_user("user1")` | returns `2`; the backup is still there, and this time no name is taken |
| `storage.backup_user("admin")` | returns `None`; the administrator has no backups |
| `storage.add_user("user2", 50)` | returns `True` |
| `storage.add_file_by("user2", "/d.txt", 5)` | returns `45` |
| `storage.restore_user("user2")` | returns `0`; user2 never made a backup, so all its files are deleted |
| `storage.get_file_size("/d.txt")` | returns `None` |
