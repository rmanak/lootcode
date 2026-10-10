"""Input-constraint validator for problem 'accounts-merge'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-written: also enforces "all accounts of the same person have the same
name": accounts linked by a shared email must carry the same name, otherwise the
merged account's name is ambiguous.
The generated version skipped this as a "semantic guarantee", which let the
retired test generator bake in a malformed hidden case. Do not regenerate.
"""
def validate_input(accounts):
    if not isinstance(accounts, list):
        return False
    if len(accounts) < 1 or len(accounts) > 1000:
        return False
    for account in accounts:
        if not isinstance(account, list):
            return False
        if len(account) < 2:
            return False
        for item in account:
            if not isinstance(item, str):
                return False
        emails = account[1:]
        for email in emails:
            if email != email.lower():
                return False
        if len(emails) != len(set(emails)):
            return False

    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for account in accounts:
        for email in account[2:]:
            parent[find(email)] = find(account[1])
    name_of = {}
    for account in accounts:
        root = find(account[1])
        if name_of.setdefault(root, account[0]) != account[0]:
            return False
    return True
