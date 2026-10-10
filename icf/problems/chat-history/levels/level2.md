A chat screen shows a whole conversation, not one message at a time. Implement
operations to list all of a user's messages, or only the messages whose ids
start with a given prefix.

```python
list_messages(self, user_id: str) -> list[str]
```

should return every message in the history of `user_id`, as a list of strings
in the following format:

```
["<message_id_1>(<message_1>)", "<message_id_2>(<message_2>)", ..., "<message_id_n>(<message_n>)"]
```

where messages are sorted lexicographically by their ids, and each content is
written exactly as it was stored. Returns an empty list if the user has no
messages.

```python
list_messages_by_prefix(self, user_id: str, prefix: str) -> list[str]
```

should return the messages in the history of `user_id` whose ids start with
`prefix`, in the same format and order as `list_messages`. The empty prefix
matches every message, and a prefix equal to a whole id matches that message.
Returns an empty list if no message matches.

"Lexicographically" means ordinary string comparison: uppercase letters come
before lowercase ones, and digits are compared one character at a time, so
`"msg10"` comes before `"msg9"`.

### Examples

The example below shows how these operations should work:

| Query | Explanation |
|---|---|
| `chat = ChatHistory()` | history state: `{}` |
| `chat.send_message("alice", "msg10", "Meeting at 5")` | history state: `{"alice": {"msg10": "Meeting at 5"}}` |
| `chat.send_message("alice", "msg20", "See you soon")` | stored |
| `chat.send_message("alice", "note1", "Buy groceries")` | stored |
| `chat.send_message("alice", "msg9", "Call me")` | history state: `{"alice": {"msg10": "Meeting at 5", "msg20": "See you soon", "note1": "Buy groceries", "msg9": "Call me"}}` |
| `chat.list_messages_by_prefix("alice", "msg")` | returns `["msg10(Meeting at 5)", "msg20(See you soon)", "msg9(Call me)"]`; `"msg10"` and `"msg20"` come before `"msg9"` in string order |
| `chat.list_messages("alice")` | returns `["msg10(Meeting at 5)", "msg20(See you soon)", "msg9(Call me)", "note1(Buy groceries)"]` |
| `chat.list_messages_by_prefix("bob", "")` | returns `[]`; bob has no messages |
| `chat.list_messages_by_prefix("alice", "note1")` | returns `["note1(Buy groceries)"]`; the prefix may be a whole id |
| `chat.delete_message("alice", "msg20")` | returns `True` |
| `chat.list_messages_by_prefix("alice", "msg2")` | returns `[]`; the only matching message was deleted |
