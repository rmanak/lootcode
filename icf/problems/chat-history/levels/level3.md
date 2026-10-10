Some messages should not stay forever — a one-time login code or a quick "be
right back" is only useful for a while. Support the timeline of operations and
messages that expire. Every operation from the previous levels now has an
alternative version with a `timestamp` parameter, representing when the
operation is executed, and a message can be sent with an **expiry**.

Remember that a test uses either the untimed operations or the timed ones,
never both. The untimed operations from levels 1 and 2 must keep working
exactly as before.

```python
send_message_at(self, user_id: str, message_id: str, message: str, timestamp: int) -> None
```

should store a message in the same way as `send_message`, at `timestamp`. The
message never expires — even if it replaces a message that had an expiry.
Returns nothing.

```python
send_message_with_expiry(self, user_id: str, message_id: str, message: str, timestamp: int, expiry: int) -> None
```

should store a message in the same way as `send_message_at`, except that the
message is only available for `expiry` units of time: during the interval
`[timestamp, timestamp + expiry)`. It can be read at any timestamp up to, but
not including, `timestamp + expiry`, and at exactly `timestamp + expiry` it has
expired. An `expiry` of `0` means the message has already expired. If the user
already has a message with that id, both its content and its expiry are
replaced, so the countdown starts again from the new `timestamp`. Returns
nothing.

```python
get_message_at(self, user_id: str, message_id: str, timestamp: int) -> str | None
```

should work like `get_message`, at `timestamp`. Returns `None` if the message
doesn't exist or has expired.

```python
delete_message_at(self, user_id: str, message_id: str, timestamp: int) -> bool
```

should work like `delete_message`, at `timestamp`. Returns `True` if the
message existed and had not expired, and was deleted; returns `False`
otherwise — an expired message cannot be deleted.

```python
list_messages_at(self, user_id: str, timestamp: int) -> list[str]
```

should work like `list_messages`, at `timestamp`, leaving out every message
that has expired.

```python
list_messages_by_prefix_at(self, user_id: str, prefix: str, timestamp: int) -> list[str]
```

should work like `list_messages_by_prefix`, at `timestamp`, leaving out every
message that has expired.

### Additional conditions

- An expired message behaves in every way as if it had been deleted, so its id
  can be used again.
- Whether a message has expired depends on the timestamp of the call that
  looks at it, not on the moment it was sent.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `chat = ChatHistory()` | history state: `{}` |
| `chat.send_message_with_expiry("alice", "msg1", "See you soon", 1, 10)` | history state: `{"alice": {"msg1": "See you soon"}}`, where `msg1` expires at timestamp 11 |
| `chat.send_message_at("alice", "msg2", "Good morning!", 4)` | history state: `{"alice": {"msg1": "See you soon", "msg2": "Good morning!"}}`, where `msg2` does not expire |
| `chat.get_message_at("alice", "msg1", 10)` | returns `"See you soon"`; timestamp 10 is still inside `[1, 11)` |
| `chat.list_messages_at("alice", 11)` | returns `["msg2(Good morning!)"]`; `msg1` expired at exactly 1 + 10 = 11 |
| `chat.get_message_at("alice", "msg1", 12)` | returns `None` |
| `chat.delete_message_at("alice", "msg1", 13)` | returns `False`; an expired message cannot be deleted |
| `chat.send_message_with_expiry("alice", "code", "4921", 14, 5)` | `code` expires at timestamp 19 |
| `chat.send_message_with_expiry("alice", "code", "7730", 16, 5)` | the message is replaced and the countdown restarts; `code` now expires at timestamp 21 |
| `chat.list_messages_by_prefix_at("alice", "co", 19)` | returns `["code(7730)"]`; the old expiry no longer applies |
| `chat.send_message_at("alice", "code", "7730", 20)` | `send_message_at` removes the expiry, so `code` does not expire |
| `chat.list_messages_at("alice", 100)` | returns `["code(7730)", "msg2(Good morning!)"]` |
| `chat.delete_message_at("alice", "msg2", 101)` | returns `True` |
| `chat.list_messages_at("alice", 102)` | returns `["code(7730)"]` |
