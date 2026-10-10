"""Level 2 — listing messages (visible cases)."""
from icf_testkit import case, expect


def seed(chat):
    chat.send_message("alice", "msg10", "Meeting at 5")
    chat.send_message("alice", "msg20", "See you soon")
    chat.send_message("alice", "note1", "Buy groceries")


@case("list_messages lists every message sorted by id")
def list_all(ChatHistory):
    chat = ChatHistory()
    seed(chat)
    expect(chat.list_messages("alice"),
           ["msg10(Meeting at 5)", "msg20(See you soon)", "note1(Buy groceries)"])


@case("list_messages_by_prefix keeps only the ids that start with the prefix")
def list_by_prefix(ChatHistory):
    chat = ChatHistory()
    seed(chat)
    expect(chat.list_messages_by_prefix("alice", "msg"),
           ["msg10(Meeting at 5)", "msg20(See you soon)"])


@case("a user with no messages lists as an empty list")
def empty_user(ChatHistory):
    chat = ChatHistory()
    seed(chat)
    expect(chat.list_messages_by_prefix("alice", "note"), ["note1(Buy groceries)"])
    expect(chat.list_messages_by_prefix("bob", ""), [])
    expect(chat.list_messages("bob"), [])
