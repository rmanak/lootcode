The database should be backed up from time to time, so that an operator can
roll everything back after a mistake. Introduce operations to support backing
up and restoring the database state based on timestamps. When restoring, the
lifetimes of fields with a TTL should be recalculated accordingly.

```python
backup(self, timestamp: int) -> int
```

should save the database state at the specified timestamp, including the
remaining TTL of every field that has one. The remaining TTL is how much of its
lifetime a field still had at the moment of the backup — the timestamp at which
it would expire, minus `timestamp`. Fields that have already expired at
`timestamp`, including a field that expires at exactly `timestamp`, are not
saved. Returns the number of non-empty records in the backup, meaning records
that hold at least one field that is still alive.

Backups accumulate: every call saves a new snapshot tagged with its own
timestamp, and no backup ever replaces or removes an earlier one.

```python
restore(self, timestamp: int, at_timestamp: int) -> None
```

should restore the database from the latest backup taken at or before
`at_timestamp`, replacing the entire current contents of the database. Anything
written after that backup is discarded, including records that didn't exist
when it was taken. It is guaranteed that such a backup exists, and
`at_timestamp` is never later than `timestamp`. Restoring does not remove any
backups: the same backup can be restored more than once, and an older backup
can be restored after a newer one.

Expiration times for restored fields should be recalculated according to the
timestamp of this operation. Since the database timeline always flows forward,
a restored field lives for its remaining TTL counted from `timestamp`: a field
that had 30 milliseconds left when the backup was taken expires at
`timestamp + 30`, no matter how much time has passed since the backup. Fields
without a TTL stay permanent.

After a restore, every other operation works on the restored data as usual,
and a later `backup` saves the restored state.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `db = Database()` | database state: `{}` |
| `db.set_with_ttl(1, "A", "B", "C", 10)` | database state: `{"A": {"B": "C"}}`, where `B` expires at timestamp 11 |
| `db.backup(3)` | returns `1`; saves the database state, with `B` having a remaining TTL of 11 - 3 = 8 |
| `db.set(4, "A", "D", "E")` | database state: `{"A": {"B": "C", "D": "E"}}` |
| `db.backup(5)` | returns `1`; saves the database state, with `B` having a remaining TTL of 6 |
| `db.delete(8, "A", "B")` | returns `True`; database state: `{"A": {"D": "E"}}` |
| `db.backup(9)` | returns `1`; saves the database state |
| `db.restore(10, 7)` | restores the latest backup at or before timestamp 7, which is the one from timestamp 5; database state: `{"A": {"B": "C", "D": "E"}}`, where `B` expires at timestamp 16 — its remaining TTL of 6, counted from 10 |
| `db.backup(11)` | returns `1`; saves the restored state, with `B` having a remaining TTL of 5 |
| `db.scan(15, "A")` | returns `"B(C), D(E)"` |
| `db.scan(16, "A")` | returns `"D(E)"`; `B` expired at timestamp 16 |
| `db.set(20, "X", "Y", "Z")` | database state: `{"A": {"D": "E"}, "X": {"Y": "Z"}}` |
| `db.backup(21)` | returns `2`; both records hold a live field |
| `db.restore(22, 12)` | restores the backup from timestamp 11; database state: `{"A": {"B": "C", "D": "E"}}`, where `B` expires at timestamp 27 |
| `db.get(23, "X", "Y")` | returns `None`; record `X` did not exist when that backup was taken |
| `db.get(26, "A", "B")` | returns `"C"` |
| `db.get(27, "A", "B")` | returns `None`; 5 milliseconds after the restore, `B` has expired |
