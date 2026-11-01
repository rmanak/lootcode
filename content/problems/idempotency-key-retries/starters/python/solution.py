class IdempotentLedger:
    def __init__(self, ttl):
        pass

    def charge(self, key, account, amount, now):
        """Apply amount to account at most once per idempotency key; return the response list."""
        pass

    def balance(self, account):
        """Return the account's current balance (0 if never charged)."""
        pass

    def failNext(self, mode):
        """Make the next charge call fail: mode is "before" or "after". Returns nothing."""
        pass
