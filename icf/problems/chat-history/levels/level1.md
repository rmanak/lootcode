Initially, no messages have been stored, so implement operations to store a
message in a user's history, read it back, and delete it.

```python
send_message(self, user_id: str, message_id: str, message: str) -> None
```

should store `message` under `message_id` in the history of `user_id`. If the
user already has a message with that id, its content is replaced — this is how
a message is edited. Returns nothing.

```python
get_message(self, user_id: str, message_id: str) -> str | None
```

should return the content of the message `message_id` in the history of
`user_id`, or `None` if the user has no message with that id.

```python
delete_message(self, user_id: str, message_id: str) -> bool
```

should remove the message `message_id` from the history of `user_id`. Returns
`True` if the message was deleted, or `False` if the user has no message with
that id. A deleted id can be used again later.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `chat = ChatHistory()` | history state: `{}` |
| `chat.send_message("alice", "msg1", "Hello Bob!")` | history state: `{"alice": {"msg1": "Hello Bob!"}}` |
| `chat.send_message("alice", "msg2", "How are you?")` | history state: `{"alice": {"msg1": "Hello Bob!", "msg2": "How are you?"}}` |
| `chat.send_message("bob", "msg1", "Hi Alice!")` | bob has a separate history with its own `msg1`; history state: `{"alice": {"msg1": "Hello Bob!", "msg2": "How are you?"}, "bob": {"msg1": "Hi Alice!"}}` |
| `chat.get_message("alice", "msg1")` | returns `"Hello Bob!"` |
| `chat.get_message("alice", "msg3")` | returns `None`; alice has no message `msg3` |
| `chat.send_message("alice", "msg2", "How are you doing?")` | the message already exists, so its content is replaced; history state: `{"alice": {"msg1": "Hello Bob!", "msg2": "How are you doing?"}, "bob": {"msg1": "Hi Alice!"}}` |
| `chat.delete_message("alice", "msg1")` | returns `True`; history state: `{"alice": {"msg2": "How are you doing?"}, "bob": {"msg1": "Hi Alice!"}}` |
| `chat.delete_message("alice", "msg1")` | returns `False`; the message was already deleted |
| `chat.get_message("bob", "msg1")` | returns `"Hi Alice!"`; deleting alice's `msg1` did not affect bob |
