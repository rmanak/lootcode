# Idempotency Keys: Safe Retries for a Payments API

Agents and services retry failed requests, and that is dangerous for anything
that moves money. A timeout does **not** mean the request failed. The charge
may have gone through and only the response was lost. Payment APIs solve this
with **idempotency keys**. The client sends a unique key with each logical
request and reuses it on every retry. The server executes a key at most once
and **replays** the stored outcome to later retries.

Implement the server side as the class `IdempotentLedger`:

- `IdempotentLedger(ttl)`: keys are remembered for `ttl` time units.
- `charge(key, account, amount, now)` adds `amount` (possibly negative) to
  `account`'s balance, at most once per key. Returns a response list.
- `balance(account)` returns the account's current balance, `0` if it has
  never been charged.
- `failNext(mode)` injects a failure into the **next** `charge` call. `mode`
  is `"before"` or `"after"`. Calling it again before that charge replaces
  the pending failure. Returns nothing.

**`charge(key, account, amount, now)`**, in order:

1. If a failure is pending, this call **consumes** it, whatever happens
   next. With `"before"`, the server crashed before doing anything: return
   `["error"]` with **no other effect**.
2. Look up `key`. Its stored entry is **live** if `now − storedAt < ttl`.
   Otherwise it has expired and counts as absent.
    - **Live, same request** (the same `account` and `amount`): the response
      is the stored response, replayed exactly. Nothing changes.
    - **Live, different request**: the response is `["conflict"]`. Nothing
      changes, and the stored entry stays as it was.
    - **Absent or expired**: execute. If `balance + amount < 0`, the response
      is `["declined", balance]` and the balance is unchanged. Otherwise add
      `amount` and respond `["ok", newBalance, chargeId]`, where `chargeId`
      numbers the successful executions `1, 2, 3, …` across all accounts.
      Either way, store `(account, amount, response, storedAt = now)` under
      `key`, replacing any expired entry. **Declines are stored too**: a
      decline is a final answer, not a transient error.
3. If the consumed failure was `"after"`, the work in step 2 **did
   happen**, but the response was lost: return `["timeout"]`. Otherwise
   return the response.

Replays never refresh `storedAt`. A key expires `ttl` after it was stored,
however often it is retried.

## Constraints

- `1 <= ttl <= 10⁹`
- `key` and `account` are non-empty strings of at most 20 characters
- `|amount| <= 10⁶`, and `0 <= now <= 10⁹`. `now` never decreases from one
  `charge` call to the next
- At most `2000` operations in total

## Examples

**Example 1**
```
Input:
["IdempotentLedger", "charge", "charge", "balance", "charge", "charge", "charge", "charge", "charge", "balance"]
[[100], ["k1", "alice", 50, 0], ["k1", "alice", 50, 5], ["alice"], ["k1", "alice", 70, 6], ["k2", "alice", -80, 7],
 ["k3", "alice", 100, 8], ["k2", "alice", -80, 9], ["k1", "alice", 50, 10], ["alice"]]
Output:
[null, ["ok", 50, 1], ["ok", 50, 1], 50, ["conflict"], ["declined", 50], ["ok", 150, 2], ["declined", 50],
 ["ok", 50, 1], 150]
Explanation: the retry of k1 replays the original response, so alice is
charged once. Reusing k1 for a different amount is a conflict. k2 is declined
(50 − 80 < 0), and its retry gets the same decline even though alice now has
150. The last k1 retry replays ["ok", 50, 1], the balance as it was then.
```

**Example 2**
```
Input:
["IdempotentLedger", "failNext", "charge", "balance", "charge", "failNext", "charge", "balance", "charge",
 "failNext", "charge", "balance"]
[[100], ["after"], ["p1", "bob", 30, 0], ["bob"], ["p1", "bob", 30, 1], ["before"], ["p2", "bob", 10, 2], ["bob"],
 ["p2", "bob", 10, 3], ["after"], ["p2", "bob", 10, 4], ["bob"]]
Output:
[null, null, ["timeout"], 30, ["ok", 30, 1], null, ["error"], 30, ["ok", 40, 2], null, ["timeout"], 40]
Explanation: the first charge timed out but did happen, so bob has 30, and the
client's retry receives the stored ["ok", 30, 1] without a double charge. The
"before" failure changes nothing, so p2 executes on its retry. The last
"after" failure hits a replay, which loses only the response.
```

**Example 3**
```
Input:
["IdempotentLedger", "charge", "charge", "charge", "charge", "charge", "failNext", "failNext", "charge", "balance",
 "balance"]
[[10], ["x", "carol", 5, 0], ["x", "carol", 5, 9], ["x", "carol", 5, 10], ["x", "carol", 7, 15],
 ["x", "carol", 7, 20], ["before"], ["after"], ["y", "dave", 1, 21], ["dave"], ["carol"]]
Output:
[null, ["ok", 5, 1], ["ok", 5, 1], ["ok", 10, 2], ["conflict"], ["ok", 17, 3], null, null, ["timeout"], 1, 17]
Explanation: at time 9 the key is live (9 − 0 < 10). At time 10 it has
expired, so the same request executes again and is stored at time 10. At
time 15 that new entry is live and the amount differs, so it is a conflict.
At time 20 it has expired again. The second failNext replaces the first, so
dave's charge happens but times out.
```
