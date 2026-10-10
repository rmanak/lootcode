"""Checkpoint: the reference solution after level 1 only."""


class ChatHistory:
    def __init__(self) -> None:
        self._histories: dict[str, dict[str, str]] = {}

    def send_message(self, user_id: str, message_id: str, message: str) -> None:
        self._histories.setdefault(user_id, {})[message_id] = message

    def get_message(self, user_id: str, message_id: str) -> str | None:
        return self._histories.get(user_id, {}).get(message_id)

    def delete_message(self, user_id: str, message_id: str) -> bool:
        history = self._histories.get(user_id, {})
        if message_id not in history:
            return False
        del history[message_id]
        return True
