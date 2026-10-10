"""Level 3 — expiring messages (visible cases)."""
from icf_testkit import case, expect


@case("a message with an expiry is readable until just before timestamp + expiry")
def expiry_boundary(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "msg1", "See you soon", 1, 10)
    expect(chat.get_message_at("alice", "msg1", 10), "See you soon", "still inside [1, 11)")
    expect(chat.get_message_at("alice", "msg1", 11), None, "expired at exactly 11")


@case("expired messages are left out of both lists")
def expired_not_listed(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m1", "x", 1, 5)
    chat.send_message_at("alice", "m2", "y", 2)
    expect(chat.list_messages_at("alice", 5), ["m1(x)", "m2(y)"])
    expect(chat.list_messages_at("alice", 6), ["m2(y)"])
    expect(chat.list_messages_by_prefix_at("alice", "m", 7), ["m2(y)"])


@case("send_message_at stores a message that never expires")
def permanent_message(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("alice", "m", "hello", 4)
    expect(chat.get_message_at("alice", "m", 10**9), "hello")


@case("an expired message cannot be deleted")
def expired_delete(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m", "x", 1, 3)
    expect(chat.delete_message_at("alice", "m", 4), False)
    chat.send_message_with_expiry("alice", "n", "y", 5, 3)
    expect(chat.delete_message_at("alice", "n", 6), True, "still alive at 6")
    expect(chat.get_message_at("alice", "n", 7), None)


@case("the timed operations work like the untimed ones for messages that never expire")
def timed_like_untimed(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("alice", "m1", "one", 1)
    chat.send_message_at("alice", "m2", "two", 2)
    expect(chat.get_message_at("alice", "m1", 3), "one")
    expect(chat.delete_message_at("alice", "m1", 4), True)
    expect(chat.delete_message_at("alice", "m1", 5), False)
    expect(chat.list_messages_at("alice", 6), ["m2(two)"])
    expect(chat.list_messages_by_prefix_at("alice", "m2", 7), ["m2(two)"])
