class IdempotentLedger:
    def __init__(self, ttl):
        self.ttl = ttl
        self.balances = {}
        self.entries = {}            # key -> (account, amount, response, storedAt)
        self.charges = 0             # successful executions so far; the next charge id is this + 1
        self.pending = None          # injected failure for the next charge: "before" / "after" / None

    def failNext(self, mode):
        self.pending = mode          # a second call before the next charge replaces the first

    def balance(self, account):
        return self.balances.get(account, 0)

    def charge(self, key, account, amount, now):
        failure, self.pending = self.pending, None
        if failure == "before":
            return ["error"]         # crashed before doing anything: no effect at all

        entry = self.entries.get(key)
        if entry is not None and now - entry[3] < self.ttl:
            if (entry[0], entry[1]) == (account, amount):
                response = entry[2]                  # a retry: replay the original outcome
            else:
                response = ["conflict"]              # key reused for a different request
        else:
            current = self.balance(account)
            if current + amount < 0:
                response = ["declined", current]     # a business outcome, so it is cached too
            else:
                self.balances[account] = current + amount
                self.charges += 1
                response = ["ok", current + amount, self.charges]
            self.entries[key] = (account, amount, response, now)

        if failure == "after":
            return ["timeout"]       # the work above happened; only the response was lost
        return list(response)
