"""Level 4 — backup and restore (visible cases)."""
from icf_testkit import case, expect


@case("zip_messages counts the live messages of every user")
def zip_counts(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("alice", "a", "x", 1)
    chat.send_message_at("alice", "b", "y", 2)
    chat.send_message_with_expiry("bob", "c", "z", 3, 47)   # expires at 50
    expect(chat.zip_messages(10), 3)
    expect(chat.zip_messages(60), 2, "bob's message expired at 50")


@case("unzip_messages restores the latest backup at or before backup_timestamp")
def unzip_picks_latest(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("alice", "m1", "v1", 1)
    chat.zip_messages(2)
    chat.send_message_at("alice", "m1", "v2", 3)
    chat.zip_messages(4)
    chat.send_message_at("alice", "m1", "v3", 5)
    chat.unzip_messages(6, 3)
    expect(chat.get_message_at("alice", "m1", 7), "v1", "the backup from 2")
    chat.unzip_messages(8, 4)
    expect(chat.get_message_at("alice", "m1", 9), "v2", "the backup from 4")


@case("a restored message's expiry resumes from the unzip timestamp")
def expiry_resumes(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("bob", "msg1", "Meeting at 5", 60, 30)   # expires at 90
    expect(chat.zip_messages(70), 1)                                        # 20 left
    chat.unzip_messages(100, 70)
    expect(chat.get_message_at("bob", "msg1", 119), "Meeting at 5", "now expires at 120")
    expect(chat.get_message_at("bob", "msg1", 120), None)


@case("messages sent after the backup are gone, and deletions are undone")
def unzip_replaces_everything(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("alice", "keep", "old", 1)
    chat.zip_messages(2)
    chat.send_message_at("alice", "new", "later", 3)
    expect(chat.delete_message_at("alice", "keep", 4), True)
    chat.unzip_messages(5, 2)
    expect(chat.list_messages_at("alice", 6), ["keep(old)"])
