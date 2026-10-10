"""Level 1 — messages (visible cases)."""
from icf_testkit import case, expect


@case("send_message stores a message that get_message reads back")
def send_and_get(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "msg1", "Hello Bob!")
    expect(chat.get_message("alice", "msg1"), "Hello Bob!")


@case("sending again under the same id replaces the message")
def resend_replaces(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "msg1", "Helo")
    chat.send_message("alice", "msg1", "Hello")
    expect(chat.get_message("alice", "msg1"), "Hello")


@case("get_message returns None for an unknown message or user")
def get_missing(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "msg1", "Hello Bob!")
    expect(chat.get_message("alice", "msg1"), "Hello Bob!")
    expect(chat.get_message("alice", "msg3"), None, "no such message")
    expect(chat.get_message("bob", "msg1"), None, "bob has no messages")


@case("delete_message removes the message and reports whether it did")
def delete_reports(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "msg1", "Hello Bob!")
    expect(chat.delete_message("alice", "msg1"), True)
    expect(chat.get_message("alice", "msg1"), None)
    expect(chat.delete_message("alice", "msg1"), False, "already deleted")


@case("every user has a separate history")
def separate_histories(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "msg1", "Hi Bob")
    chat.send_message("bob", "msg1", "Hi Alice")
    expect(chat.get_message("alice", "msg1"), "Hi Bob")
    expect(chat.get_message("bob", "msg1"), "Hi Alice")
    expect(chat.delete_message("alice", "msg1"), True)
    expect(chat.get_message("bob", "msg1"), "Hi Alice", "bob's message is untouched")
