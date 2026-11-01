"""Input-constraint validator for problem 'conversation-memory-window'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks the operation sequence and every stated bound:
- operations and args are aligned lists of length 1..2000
- the constructor `ConversationMemory` comes exactly once, first, with args
  [maxTokens, placeholderTokens]: ints in [1, 10^5] and [0, 100]
- every later operation is add, getContext or contextTokens
- add takes [role, text, tokens]: role one of system/user/assistant/tool,
  text a string of at most 200 characters, tokens an int in [1, 10^4]
- system messages come before every other message; a tool message directly
  follows an assistant or tool message
- getContext and contextTokens take []
"""

ROLES = {"system", "user", "assistant", "tool"}


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def validate_input(operations, args):
    if not (isinstance(operations, list) and isinstance(args, list)):
        return False
    if not 1 <= len(operations) <= 2000 or len(args) != len(operations):
        return False
    if operations[0] != "ConversationMemory" or not isinstance(args[0], list) or len(args[0]) != 2:
        return False
    if not (_int(args[0][0], 1, 10**5) and _int(args[0][1], 0, 100)):
        return False
    prev = None                              # role of the previous add
    for op, a in zip(operations[1:], args[1:]):
        if not isinstance(a, list):
            return False
        if op in ("getContext", "contextTokens"):
            if a:
                return False
        elif op == "add":
            if len(a) != 3:
                return False
            role, text, tokens = a
            if role not in ROLES or not isinstance(text, str) or len(text) > 200 or not _int(tokens, 1, 10**4):
                return False
            if role == "system" and prev not in (None, "system"):
                return False
            if role == "tool" and prev not in ("assistant", "tool"):
                return False
            prev = role
        else:
            return False
    return True
