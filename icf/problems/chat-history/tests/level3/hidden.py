"""Level 3 — expiring messages (hidden cases)."""
import random

from icf_testkit import case, expect


@case("sending again replaces both the content and the expiry")
def resend_replaces_expiry(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m", "v1", 1, 100)
    chat.send_message_with_expiry("alice", "m", "v2", 10, 5)
    expect(chat.get_message_at("alice", "m", 14), "v2")
    expect(chat.get_message_at("alice", "m", 15), None, "the shorter expiry replaced the longer one")
    chat.send_message_with_expiry("alice", "n", "x", 20, 5)
    chat.send_message_with_expiry("alice", "n", "y", 24, 10)
    expect(chat.get_message_at("alice", "n", 30), "y", "the countdown restarted at 24")


@case("send_message_at removes an existing expiry")
def send_at_removes_expiry(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m", "x", 1, 5)
    chat.send_message_at("alice", "m", "y", 3)
    expect(chat.get_message_at("alice", "m", 1000), "y")


@case("an expiry of 0 means the message is already gone")
def zero_expiry(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m", "x", 5, 0)
    expect(chat.get_message_at("alice", "m", 5), None)
    expect(chat.list_messages_at("alice", 6), [])
    chat.send_message_at("alice", "n", "y", 7)
    expect(chat.list_messages_at("alice", 8), ["n(y)"])


@case("an expired message id can be used again")
def reuse_expired_id(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m", "old", 1, 2)
    expect(chat.get_message_at("alice", "m", 3), None)
    chat.send_message_at("alice", "m", "new", 4)
    expect(chat.get_message_at("alice", "m", 5), "new")


@case("each message has its own expiry")
def per_message_expiry(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m1", "x", 1, 10)
    chat.send_message_with_expiry("alice", "m2", "y", 2, 20)
    chat.send_message_with_expiry("bob", "m1", "z", 3, 5)
    expect(chat.list_messages_at("alice", 9), ["m1(x)", "m2(y)"])
    expect(chat.list_messages_at("bob", 9), [])
    expect(chat.list_messages_at("alice", 12), ["m2(y)"])


@case("a user whose messages all expired lists as empty but can still receive messages")
def all_expired(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "a", "1", 1, 2)
    chat.send_message_with_expiry("alice", "b", "2", 2, 2)
    expect(chat.list_messages_at("alice", 3), ["b(2)"])
    expect(chat.list_messages_by_prefix_at("alice", "", 4), [])
    chat.send_message_at("alice", "c", "3", 5)
    expect(chat.list_messages_at("alice", 6), ["c(3)"])


@case("expiry is checked at the moment of each call")
def expiry_per_call(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m", "x", 10, 10)
    expect(chat.list_messages_at("alice", 19), ["m(x)"])
    expect(chat.get_message_at("alice", "m", 20), None)
    expect(chat.list_messages_by_prefix_at("alice", "m", 21), [])


@case("timed messages match a reference model over a random workload")
def fuzz_against_model(ChatHistory):
    rng = random.Random(77)
    chat = ChatHistory()
    model = {}   # (user, id) -> (content, expires | None)
    timestamp = 0

    def alive(key):
        return key in model and (model[key][1] is None or timestamp < model[key][1])

    for step in range(800):
        timestamp += rng.randrange(1, 5)
        user = rng.choice(["alice", "bob"])
        message_id = rng.choice(["m1", "m2", "m10", "n"])
        key = (user, message_id)
        roll = rng.random()
        if roll < 0.3:
            expiry = rng.randrange(0, 25)
            content = f"c{step}"
            chat.send_message_with_expiry(user, message_id, content, timestamp, expiry)
            model[key] = (content, timestamp + expiry)
        elif roll < 0.4:
            content = f"p{step}"
            chat.send_message_at(user, message_id, content, timestamp)
            model[key] = (content, None)
        elif roll < 0.55:
            ok = alive(key)
            expect(chat.delete_message_at(user, message_id, timestamp), ok,
                   f"delete_message_at({user}, {message_id}, {timestamp})")
            if ok:
                del model[key]
        elif roll < 0.75:
            want = model[key][0] if alive(key) else None
            expect(chat.get_message_at(user, message_id, timestamp), want,
                   f"get_message_at({user}, {message_id}, {timestamp})")
        else:
            prefix = rng.choice(["", "m", "m1", "n"])
            live = sorted(k[1] for k in model if k[0] == user and alive(k))
            want = [f"{m}({model[(user, m)][0]})" for m in live if m.startswith(prefix)]
            expect(chat.list_messages_by_prefix_at(user, prefix, timestamp), want,
                   f"list_messages_by_prefix_at({user}, {prefix!r}, {timestamp})")
