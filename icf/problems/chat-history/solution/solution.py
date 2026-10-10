"""Reference solution — all four levels.

Every message is stored with the moment it expires, where ``None`` means it
never does. Two consequences keep the later levels small:

* the untimed level-1/2 methods are simply the timed ones called at timestamp
  0 — a test never mixes the two, and a message sent without a timestamp never
  expires, so any moment gives the same answer;
* a backup holds the same messages with the absolute ``expires_at`` rewritten
  as the time *remaining*, which a restore turns back into an absolute moment
  counted from its own timestamp.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Message:
    """A message in a user's history. `expires_at` of None means it never does."""

    content: str
    expires_at: int | None = None

    def alive_at(self, timestamp: int) -> bool:
        return self.expires_at is None or timestamp < self.expires_at

    def saved_at(self, timestamp: int) -> "SavedMessage":
        """This message as a backup entry: a lifetime left, not a moment."""
        remaining = (None if self.expires_at is None
                     else self.expires_at - timestamp)
        return SavedMessage(self.content, remaining)


@dataclass(slots=True)
class SavedMessage:
    """A message inside a backup: what was *left* of its life when it was taken."""

    content: str
    remaining: int | None = None

    def restored_at(self, timestamp: int) -> Message:
        """The message again, its remaining life resuming from `timestamp`."""
        expires_at = (None if self.remaining is None
                      else timestamp + self.remaining)
        return Message(self.content, expires_at)


@dataclass(slots=True)
class Backup:
    """Every live message at the moment `zip_messages` was called."""

    taken_at: int
    histories: dict[str, dict[str, SavedMessage]]


class ChatHistory:
    def __init__(self) -> None:
        self._histories: dict[str, dict[str, Message]] = {}
        self._backups: list[Backup] = []     # appended in timestamp order

    # --- helpers -----------------------------------------------------------

    def _listing(self, user_id: str, prefix: str, timestamp: int) -> list[str]:
        history = self._histories.get(user_id, {})
        return [f"{message_id}({message.content})"
                for message_id, message in sorted(history.items())
                if message_id.startswith(prefix) and message.alive_at(timestamp)]

    # --- Level 1 -----------------------------------------------------------

    def send_message(self, user_id: str, message_id: str, message: str) -> None:
        self.send_message_at(user_id, message_id, message, 0)

    def get_message(self, user_id: str, message_id: str) -> str | None:
        return self.get_message_at(user_id, message_id, 0)

    def delete_message(self, user_id: str, message_id: str) -> bool:
        return self.delete_message_at(user_id, message_id, 0)

    # --- Level 2 -----------------------------------------------------------

    def list_messages(self, user_id: str) -> list[str]:
        return self._listing(user_id, "", 0)

    def list_messages_by_prefix(self, user_id: str, prefix: str) -> list[str]:
        return self._listing(user_id, prefix, 0)

    # --- Level 3 -----------------------------------------------------------

    def send_message_at(self, user_id: str, message_id: str, message: str,
                        timestamp: int) -> None:
        self._histories.setdefault(user_id, {})[message_id] = Message(message)

    def send_message_with_expiry(self, user_id: str, message_id: str, message: str,
                                 timestamp: int, expiry: int) -> None:
        self._histories.setdefault(user_id, {})[message_id] = Message(
            message, timestamp + expiry)

    def get_message_at(self, user_id: str, message_id: str,
                       timestamp: int) -> str | None:
        message = self._histories.get(user_id, {}).get(message_id)
        if message is None or not message.alive_at(timestamp):
            return None
        return message.content

    def delete_message_at(self, user_id: str, message_id: str,
                          timestamp: int) -> bool:
        if self.get_message_at(user_id, message_id, timestamp) is None:
            return False
        del self._histories[user_id][message_id]
        return True

    def list_messages_at(self, user_id: str, timestamp: int) -> list[str]:
        return self._listing(user_id, "", timestamp)

    def list_messages_by_prefix_at(self, user_id: str, prefix: str,
                                   timestamp: int) -> list[str]:
        return self._listing(user_id, prefix, timestamp)

    # --- Level 4 -----------------------------------------------------------

    def zip_messages(self, timestamp: int) -> int:
        snapshot: dict[str, dict[str, SavedMessage]] = {}
        saved = 0
        for user_id, history in self._histories.items():
            live = {message_id: message.saved_at(timestamp)
                    for message_id, message in history.items()
                    if message.alive_at(timestamp)}
            if live:
                snapshot[user_id] = live
                saved += len(live)
        self._backups.append(Backup(timestamp, snapshot))
        return saved

    def unzip_messages(self, timestamp: int, backup_timestamp: int) -> None:
        chosen = None
        for backup in self._backups:
            if backup.taken_at <= backup_timestamp:
                chosen = backup
        if chosen is None:
            return
        self._histories = {
            user_id: {message_id: saved.restored_at(timestamp)
                      for message_id, saved in history.items()}
            for user_id, history in chosen.histories.items()
        }
