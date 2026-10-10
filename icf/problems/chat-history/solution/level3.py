"""Checkpoint: the reference solution after levels 1 to 3 (no backups yet)."""

from dataclasses import dataclass


@dataclass(slots=True)
class Message:
    """A message in a user's history. `expires_at` of None means it never does."""

    content: str
    expires_at: int | None = None

    def alive_at(self, timestamp: int) -> bool:
        return self.expires_at is None or timestamp < self.expires_at


class ChatHistory:
    def __init__(self) -> None:
        self._histories: dict[str, dict[str, Message]] = {}

    def send_message(self, user_id: str, message_id: str, message: str) -> None:
        self.send_message_at(user_id, message_id, message, 0)

    def get_message(self, user_id: str, message_id: str) -> str | None:
        return self.get_message_at(user_id, message_id, 0)

    def delete_message(self, user_id: str, message_id: str) -> bool:
        return self.delete_message_at(user_id, message_id, 0)

    def list_messages(self, user_id: str) -> list[str]:
        return self.list_messages_by_prefix_at(user_id, "", 0)

    def list_messages_by_prefix(self, user_id: str, prefix: str) -> list[str]:
        return self.list_messages_by_prefix_at(user_id, prefix, 0)

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
        return self.list_messages_by_prefix_at(user_id, "", timestamp)

    def list_messages_by_prefix_at(self, user_id: str, prefix: str,
                                   timestamp: int) -> list[str]:
        history = self._histories.get(user_id, {})
        return [f"{message_id}({message.content})"
                for message_id, message in sorted(history.items())
                if message_id.startswith(prefix) and message.alive_at(timestamp)]
