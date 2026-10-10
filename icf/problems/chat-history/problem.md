### Instructions

Your task is to implement a simplified version of the message storage behind a
chat application. Every user has a message history: each message is stored
under a message id, so it can be read back, edited by sending it again under
the same id, deleted, and shown in a list. Later, messages can be sent so that
they disappear after a while — like the disappearing messages many chat apps
offer — and the whole service can be backed up and restored. All operations
that should be supported are described in the levels below.

Solving this task consists of several levels. Each subsequent level is opened
when the current level is correctly solved, and you always have access to the
statements of the current and all previous levels.

### Requirements

Implement the class `ChatHistory`. Plan your design according to the level
specifications below:

- **Level 1:** The chat history should support storing, reading and deleting a
  user's messages.
- **Level 2:** The chat history should support listing a user's messages, all
  of them or only those whose ids start with a given prefix.
- **Level 3:** The chat history should support a timeline of operations and
  messages that expire.
- **Level 4:** The chat history should support backing up every user's
  messages and restoring them from a backup.

To move to the next level, you need to pass all the tests at the current level —
visible and hidden. Your code carries forward from one level to the next, and
the tests of every level you have already passed are re-run on each submission,
so plan a data model you can extend rather than one you will have to replace.

### The data model

Each **user** has their own message history, which maps **message ids** to
**message contents**, both strings. For example:

```
"alice"  →  {"msg1": "Hello Bob!", "msg2": "How are you?"}
```

A message id is unique within one user's history; different users may use the
same ids without affecting each other. Users do not need to be registered: a
user's history exists as soon as they are sent a message, and a user who has
no messages simply has an empty history.

### Notes

- Levels 1 and 2 have no timestamps. Level 3 adds a timed version of every
  operation, which takes the `timestamp` at which it happens. Timestamps are
  non-negative integers and strictly increase from one call to the next within
  a test.
- A test uses either the untimed operations or the timed ones, never both —
  but the untimed operations must keep working exactly as before.
- User ids and message ids are non-empty strings. Message contents are strings
  and may be empty — an empty message is still a message.
- Every call is valid: you never need to raise errors or validate argument
  types.
- A fresh `ChatHistory()` holds no messages.
