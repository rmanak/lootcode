The chat service should be backed up from time to time, so that message
histories can be recovered after a failure. Introduce operations to back up
("zip") the messages of every user and to restore ("unzip") them from a backup.
When restoring, expiry times should be recalculated.

```python
zip_messages(self, timestamp: int) -> int
```

should save the messages of all users as they are at `timestamp`, including the
**remaining expiry** of every message that has one — how much time the message
still had left at the moment of the backup, i.e. the timestamp at which it
would expire minus `timestamp`. Messages that have already expired at
`timestamp`, including a message that expires at exactly `timestamp`, are not
saved. Returns the number of messages saved, counted across all users.

Backups accumulate: every call saves a new backup tagged with its own
timestamp, and no backup ever replaces or removes an earlier one.

```python
unzip_messages(self, timestamp: int, backup_timestamp: int) -> None
```

should restore the messages of all users from the latest backup taken at or
before `backup_timestamp`, replacing every user's current messages. Anything
sent after that backup is discarded, and anything deleted since then comes
back. It is guaranteed that such a backup exists, and `backup_timestamp` is
never later than `timestamp`. Restoring does not remove any backups: the same
backup can be restored more than once, and an older backup can be restored
after a newer one. Returns nothing.

Expiry times of restored messages should be recalculated according to the
timestamp of this operation: since the timeline always flows forward, a
restored message expires its remaining expiry **after `timestamp`**. A message
that had 20 units of time left when it was backed up expires at
`timestamp + 20`, no matter how much time has passed since the backup. Messages
that never expire stay that way.

After a restore, every other operation works on the restored messages as
usual, and a later `zip_messages` saves the restored state.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `chat = ChatHistory()` | history state: `{}` |
| `chat.send_message_with_expiry("bob", "msg1", "Meeting at 5", 60, 30)` | history state: `{"bob": {"msg1": "Meeting at 5"}}`, where `msg1` expires at timestamp 90 |
| `chat.send_message_at("alice", "lunch", "Lunch?", 65)` | history state: `{"bob": {"msg1": "Meeting at 5"}, "alice": {"lunch": "Lunch?"}}` |
| `chat.zip_messages(70)` | returns `2`; saves both messages, with bob's `msg1` having a remaining expiry of 20 |
| `chat.send_message_with_expiry("bob", "msg2", "Dinner at 8", 75, 20)` | `msg2` expires at timestamp 95 |
| `chat.delete_message_at("alice", "lunch", 80)` | returns `True` |
| `chat.zip_messages(95)` | returns `0`; bob's `msg1` expired at 90, `msg2` expires at exactly 95, and alice's message was deleted |
| `chat.unzip_messages(100, 70)` | restores the backup from timestamp 70; history state: `{"bob": {"msg1": "Meeting at 5"}, "alice": {"lunch": "Lunch?"}}`, where `msg1` expires at timestamp 120 — its remaining 20, counted from 100 |
| `chat.list_messages_at("bob", 100)` | returns `["msg1(Meeting at 5)"]`; `msg2` was sent after the backup, so it is gone |
| `chat.get_message_at("alice", "lunch", 101)` | returns `"Lunch?"`; the deletion at 80 is undone |
| `chat.list_messages_at("bob", 119)` | returns `["msg1(Meeting at 5)"]` |
| `chat.list_messages_at("bob", 120)` | returns `[]`; the restored message has expired |
| `chat.unzip_messages(130, 99)` | restores the backup from timestamp 95, which saved no messages; history state: `{}` |
| `chat.list_messages_at("alice", 131)` | returns `[]` |
