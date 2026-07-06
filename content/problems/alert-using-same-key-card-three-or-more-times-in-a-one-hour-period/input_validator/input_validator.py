"""Input-constraint validator for problem 'alert-using-same-key-card-three-or-more-times-in-a-one-hour-period'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(keyName, keyTime):
    if not isinstance(keyName, list) or not isinstance(keyTime, list):
        return False

    if len(keyName) != len(keyTime):
        return False

    n = len(keyName)
    if n < 1 or n > 100000:
        return False

    seen_pairs = set()

    for i in range(n):
        name = keyName[i]
        time = keyTime[i]

        if not isinstance(name, str) or not isinstance(time, str):
            return False

        if not name or not all(c.islower() for c in name):
            return False

        if len(time) != 5 or time[2] != ':':
            return False

        if not time[0:2].isdigit() or not time[3:5].isdigit():
            return False

        hh = int(time[0:2])
        mm = int(time[3:5])
        if hh < 0 or hh > 23 or mm < 0 or mm > 59:
            return False

        pair = (name, time)
        if pair in seen_pairs:
            return False
        seen_pairs.add(pair)

    return True
