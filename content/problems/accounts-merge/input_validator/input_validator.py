"""Input-constraint validator for problem 'accounts-merge'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
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
    return True
