Design a sliding-window rate limiter that allows at most `limit` requests **per
user** within any `window` seconds.

Implement the `RateLimiter` class:

- `RateLimiter(int limit, int window)` initializes the limiter with the given
  per-user allowance and window length (in seconds).
- `boolean request(String userId, int timestamp)` returns `true` if the request is
  allowed — that is, fewer than `limit` of that user's **allowed** requests have
  timestamps in `(timestamp - window, timestamp]` — and records it. Otherwise the
  request is rejected and `false` is returned; a rejected request is not recorded.

Calls are made in chronological order, so `timestamp` is non-decreasing. Users are
limited independently of one another.

**Example 1:**

```
Input
["RateLimiter", "request", "request", "request", "request"]
[[2, 10], ["a", 1], ["a", 2], ["a", 3], ["a", 11]]

Output
[null, true, true, false, true]
```

Explanation: with `limit = 2` and `window = 10`, the third request at `3` is
rejected because the requests at `1` and `2` are still in the window; by `11` the
request at `1` has expired, so the request is allowed.

**Example 2:**

```
Input
["RateLimiter", "request", "request", "request"]
[[1, 5], ["a", 1], ["b", 1], ["a", 2]]

Output
[null, true, true, false]
```

Explanation: `a` and `b` have separate allowances, so `b`'s request at `1` is
allowed; `a`'s second request at `2` is not.

**Constraints:**

- `1 <= limit <= 10⁴`, `1 <= window <= 10⁹`
- `0 <= timestamp <= 10⁹`, non-decreasing across calls.
- At most `10⁵` calls will be made to `request`.
