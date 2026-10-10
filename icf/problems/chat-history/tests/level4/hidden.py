"""Level 4 — backup and restore (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a message expiring exactly at the zip timestamp is not saved")
def expiring_at_zip(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("alice", "m", "x", 1, 9)   # expires at 10
    chat.send_message_at("alice", "p", "y", 2)
    expect(chat.zip_messages(10), 1)
    chat.unzip_messages(11, 10)
    expect(chat.list_messages_at("alice", 12), ["p(y)"])


@case("backups survive being restored, and can be restored out of order")
def backups_survive(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("a", "m", "v1", 1)
    chat.zip_messages(2)
    chat.send_message_at("a", "m", "v2", 3)
    chat.zip_messages(4)
    chat.unzip_messages(5, 4)
    expect(chat.get_message_at("a", "m", 6), "v2")
    chat.unzip_messages(7, 2)
    expect(chat.get_message_at("a", "m", 8), "v1", "the older backup is still there")
    chat.unzip_messages(10, 9)
    expect(chat.get_message_at("a", "m", 11), "v2", "and so is the newer one")


@case("messages that never expire come back never expiring")
def permanent_restored(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("a", "m", "forever", 1)
    chat.zip_messages(2)
    chat.unzip_messages(1000, 2)
    expect(chat.get_message_at("a", "m", 10**9), "forever")


@case("a zip taken after an unzip saves the restored state")
def zip_after_unzip(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("a", "x", "v", 1, 10)   # expires at 11
    expect(chat.zip_messages(5), 1)                       # 6 left
    chat.unzip_messages(20, 5)                            # expires at 26
    expect(chat.zip_messages(22), 1)                      # 4 left
    chat.send_message_at("a", "y", "later", 23)
    chat.unzip_messages(100, 22)                          # expires at 104
    expect(chat.list_messages_at("a", 103), ["x(v)"])
    expect(chat.get_message_at("a", "x", 104), None)


@case("zip_messages counts messages, not users")
def counts_messages(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("a", "m1", "x", 1)
    chat.send_message_at("a", "m2", "x", 2)
    chat.send_message_at("a", "m3", "x", 3)
    expect(chat.zip_messages(4), 3)


@case("restoring a backup that saved nothing clears every history")
def restore_empty_backup(ChatHistory):
    chat = ChatHistory()
    expect(chat.zip_messages(1), 0)
    chat.send_message_at("a", "m", "x", 2)
    expect(chat.get_message_at("a", "m", 3), "x")
    chat.unzip_messages(4, 1)
    expect(chat.list_messages_at("a", 5), [])
    expect(chat.get_message_at("a", "m", 6), None)


@case("restoring the same backup twice gives the same result")
def restore_twice(ChatHistory):
    chat = ChatHistory()
    chat.send_message_with_expiry("a", "m", "x", 1, 20)   # expires at 21
    chat.zip_messages(5)                                  # 16 left
    chat.send_message_at("a", "n", "y", 6)
    chat.unzip_messages(10, 5)                            # expires at 26
    expect(chat.get_message_at("a", "m", 25), "x")
    chat.unzip_messages(30, 5)                            # expires at 46
    expect(chat.list_messages_at("a", 45), ["m(x)"])
    expect(chat.list_messages_at("a", 46), [])


@case("everything keeps working on restored messages")
def works_after_restore(ChatHistory):
    chat = ChatHistory()
    chat.send_message_at("a", "m1", "x", 1)
    chat.send_message_at("a", "m2", "y", 2)
    chat.zip_messages(3)
    chat.unzip_messages(4, 3)
    expect(chat.delete_message_at("a", "m1", 5), True)
    chat.send_message_with_expiry("a", "m3", "z", 6, 4)   # expires at 10
    expect(chat.list_messages_at("a", 7), ["m2(y)", "m3(z)"])
    expect(chat.list_messages_by_prefix_at("a", "m3", 10), [])
    expect(chat.zip_messages(11), 1)


@case("backups and restores match a reference model over a random workload")
def fuzz_against_model(ChatHistory):
    rng = random.Random(88)
    chat = ChatHistory()
    model = {}     # (user, id) -> (content, expires | None)
    backups = []   # (timestamp, {(user, id): (content, remaining | None)})
    timestamp = 0

    def alive(key):
        return key in model and (model[key][1] is None or timestamp < model[key][1])

    for step in range(900):
        timestamp += rng.randrange(1, 5)
        user = rng.choice(["alice", "bob", "cy"])
        message_id = rng.choice(["m1", "m2", "n"])
        key = (user, message_id)
        roll = rng.random()
        if roll < 0.25:
            expiry = rng.randrange(0, 40)
            chat.send_message_with_expiry(user, message_id, f"e{step}", timestamp, expiry)
            model[key] = (f"e{step}", timestamp + expiry)
        elif roll < 0.35:
            chat.send_message_at(user, message_id, f"p{step}", timestamp)
            model[key] = (f"p{step}", None)
        elif roll < 0.45:
            ok = alive(key)
            expect(chat.delete_message_at(user, message_id, timestamp), ok,
                   f"delete_message_at({user}, {message_id}, {timestamp})")
            if ok:
                del model[key]
        elif roll < 0.58:
            want = model[key][0] if alive(key) else None
            expect(chat.get_message_at(user, message_id, timestamp), want,
                   f"get_message_at({user}, {message_id}, {timestamp})")
        elif roll < 0.7:
            live = sorted(k[1] for k in model if k[0] == user and alive(k))
            expect(chat.list_messages_at(user, timestamp),
                   [f"{m}({model[(user, m)][0]})" for m in live],
                   f"list_messages_at({user}, {timestamp})")
        elif roll < 0.85:
            snapshot = {k: (v[0], None if v[1] is None else v[1] - timestamp)
                        for k, v in model.items() if alive(k)}
            expect(chat.zip_messages(timestamp), len(snapshot), f"zip_messages({timestamp})")
            backups.append((timestamp, snapshot))
        elif backups:
            backup_timestamp = rng.randrange(backups[0][0], timestamp + 1)
            chosen = [snap for taken_at, snap in backups if taken_at <= backup_timestamp][-1]
            chat.unzip_messages(timestamp, backup_timestamp)
            model = {k: (content, None if remaining is None else timestamp + remaining)
                     for k, (content, remaining) in chosen.items()}
