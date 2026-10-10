"""Level 2 — listing messages (hidden cases)."""
import random

from icf_testkit import case, expect


@case("the empty prefix matches every message")
def empty_prefix(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "b", "2")
    chat.send_message("alice", "a", "1")
    expect(chat.list_messages_by_prefix("alice", ""), ["a(1)", "b(2)"])


@case("ids sort as plain strings: msg10 before msg9, and capitals first")
def plain_string_order(ChatHistory):
    chat = ChatHistory()
    for message_id in ("msg9", "msg10", "Msg1", "m"):
        chat.send_message("alice", message_id, "x")
    expect(chat.list_messages("alice"), ["Msg1(x)", "m(x)", "msg10(x)", "msg9(x)"])


@case("a deleted message disappears and a replaced one shows its new content")
def list_after_changes(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "a", "old")
    chat.send_message("alice", "b", "keep")
    chat.send_message("alice", "a", "new")
    chat.send_message("alice", "c", "gone")
    chat.delete_message("alice", "c")
    expect(chat.list_messages("alice"), ["a(new)", "b(keep)"])


@case("lists never include another user's messages")
def lists_are_per_user(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "m1", "from alice")
    chat.send_message("bob", "m2", "from bob")
    expect(chat.list_messages("alice"), ["m1(from alice)"])
    expect(chat.list_messages_by_prefix("bob", "m"), ["m2(from bob)"])


@case("a prefix equal to a whole id matches that message")
def whole_id_prefix(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "msg", "short")
    chat.send_message("alice", "msg1", "long")
    expect(chat.list_messages_by_prefix("alice", "msg"), ["msg(short)", "msg1(long)"])
    expect(chat.list_messages_by_prefix("alice", "msg1"), ["msg1(long)"])
    expect(chat.list_messages_by_prefix("alice", "msg12"), [])


@case("a user whose messages were all deleted lists as empty")
def all_deleted(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "m", "x")
    expect(chat.list_messages("alice"), ["m(x)"])
    chat.delete_message("alice", "m")
    expect(chat.list_messages("alice"), [])


@case("content with parentheses, commas and nothing at all is listed verbatim")
def verbatim_listing(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "a", "x(y), z")
    chat.send_message("alice", "b", "")
    expect(chat.list_messages("alice"), ["a(x(y), z)", "b()"])


@case("listings match a reference model over a random workload")
def fuzz_against_model(ChatHistory):
    rng = random.Random(66)
    chat = ChatHistory()
    model = {}
    ids = ["msg1", "msg10", "msg2", "note", "Msg", "n"]
    for step in range(600):
        user = rng.choice(["alice", "bob"])
        roll = rng.random()
        if roll < 0.4:
            message_id = rng.choice(ids)
            content = rng.choice(["hi", "", "(x)", f"s{step}"])
            chat.send_message(user, message_id, content)
            model.setdefault(user, {})[message_id] = content
        elif roll < 0.55:
            message_id = rng.choice(ids)
            chat.delete_message(user, message_id)
            model.get(user, {}).pop(message_id, None)
        else:
            prefix = rng.choice(["", "msg", "msg1", "n", "M", "z"])
            history = model.get(user, {})
            want = [f"{m}({history[m]})" for m in sorted(history) if m.startswith(prefix)]
            if prefix == "":
                expect(chat.list_messages(user), want, f"list_messages({user}) at step {step}")
            expect(chat.list_messages_by_prefix(user, prefix), want,
                   f"list_messages_by_prefix({user}, {prefix!r}) at step {step}")
