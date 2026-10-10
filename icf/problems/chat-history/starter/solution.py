class ChatHistory:
    """Per-user message storage for a chat application.

    Implement the methods for the level you are on; later levels are declared
    so the class stays importable. Your code carries forward — extend it.
    """

    def __init__(self) -> None:
        pass

    # --- Level 1: messages ------------------------------------------------

    def send_message(self, user_id: str, message_id: str, message: str) -> None:
        pass

    def get_message(self, user_id: str, message_id: str) -> str | None:
        pass

    def delete_message(self, user_id: str, message_id: str) -> bool:
        pass

    # --- Level 2: listing messages ----------------------------------------

    def list_messages(self, user_id: str) -> list[str]:
        pass

    def list_messages_by_prefix(self, user_id: str, prefix: str) -> list[str]:
        pass

    # --- Level 3: expiring messages ---------------------------------------

    def send_message_at(self, user_id: str, message_id: str, message: str,
                        timestamp: int) -> None:
        pass

    def send_message_with_expiry(self, user_id: str, message_id: str, message: str,
                                 timestamp: int, expiry: int) -> None:
        pass

    def get_message_at(self, user_id: str, message_id: str,
                       timestamp: int) -> str | None:
        pass

    def delete_message_at(self, user_id: str, message_id: str,
                          timestamp: int) -> bool:
        pass

    def list_messages_at(self, user_id: str, timestamp: int) -> list[str]:
        pass

    def list_messages_by_prefix_at(self, user_id: str, prefix: str,
                                   timestamp: int) -> list[str]:
        pass

    # --- Level 4: backup and restore --------------------------------------

    def zip_messages(self, timestamp: int) -> int:
        pass

    def unzip_messages(self, timestamp: int, backup_timestamp: int) -> None:
        pass
