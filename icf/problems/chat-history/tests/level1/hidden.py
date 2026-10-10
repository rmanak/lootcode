"""Level 1 — messages (hidden cases)."""
import random

from icf_testkit import case, expect


@case("a deleted message id can be used again")
def reuse_deleted_id(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "m", "first")
    chat.delete_message("alice", "m")
    chat.send_message("alice", "m", "second")
    expect(chat.get_message("alice", "m"), "second")


@case("message content is stored verbatim, even when it is empty")
def verbatim_content(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "empty", "")
    chat.send_message("alice", "odd", "a(b), c  ")
    expect(chat.get_message("alice", "empty"), "", "an empty message is still a message")
    expect(chat.get_message("alice", "odd"), "a(b), c  ")
    expect(chat.delete_message("alice", "empty"), True)


@case("message ids and user ids are case-sensitive")
def case_sensitive_ids(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "Msg", "upper")
    chat.send_message("alice", "msg", "lower")
    chat.send_message("Alice", "msg", "other user")
    expect(chat.get_message("alice", "Msg"), "upper")
    expect(chat.get_message("alice", "msg"), "lower")
    expect(chat.get_message("Alice", "msg"), "other user")
    expect(chat.get_message("Alice", "Msg"), None)


@case("a refused delete changes nothing")
def refused_delete(ChatHistory):
    chat = ChatHistory()
    chat.send_message("alice", "m1", "x")
    expect(chat.delete_message("alice", "m2"), False)
    expect(chat.delete_message("bob", "m1"), False)
    expect(chat.get_message("alice", "m1"), "x")


@case("many users and messages round-trip independently")
def many_messages(ChatHistory):
    chat = ChatHistory()
    for u in range(20):
        for m in range(5):
            chat.send_message(f"user{u}", f"m{m}", f"{u}-{m}")
    expect(chat.get_message("user7", "m3"), "7-3")
    expect(chat.get_message("user19", "m0"), "19-0")
    expect(chat.delete_message("user7", "m3"), True)
    expect(chat.get_message("user8", "m3"), "8-3")


@case("sends, reads and deletes match a reference model over a random workload")
def fuzz_against_model(ChatHistory):
    rng = random.Random(55)
    chat = ChatHistory()
    model = {}
    for step in range(700):
        user = rng.choice(["alice", "bob", "cy"])
        message_id = rng.choice(["m1", "m2", "m3", "M1"])
        roll = rng.random()
        if roll < 0.4:
            content = rng.choice(["hi", "", "hello there", f"#{step}"])
            chat.send_message(user, message_id, content)
            model[(user, message_id)] = content
        elif roll < 0.65:
            existed = (user, message_id) in model
            expect(chat.delete_message(user, message_id), existed,
                   f"delete_message({user}, {message_id}) at step {step}")
            model.pop((user, message_id), None)
        else:
            expect(chat.get_message(user, message_id), model.get((user, message_id)),
                   f"get_message({user}, {message_id}) at step {step}")
