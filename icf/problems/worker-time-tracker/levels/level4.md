To reward work during busy periods, the company sometimes pays double. Implement
an operation to declare a double-pay period, during which every worker earns
twice their usual compensation.

```python
set_double_pay(self, start_timestamp: int, end_timestamp: int) -> None
```

should declare the period `[start_timestamp, end_timestamp)` a double-pay
period: any time a worker spends in the office during it is paid at **twice**
the compensation of that session. Returns nothing.

### How `calc_salary` changes

- Within the period being calculated, every part of a session that is also
  inside a double-pay period is paid at `2 × compensation`; the rest of the
  session is paid at `compensation`, exactly as before.
- Double pay applies to every worker, and to **all** sessions — including
  sessions that took place before `set_double_pay` was called. It is a property
  of the time itself, not of the moment it was declared.
- Double-pay periods may overlap. Overlaps never stack: time covered by several
  double-pay periods is still paid at exactly twice the compensation, never
  more. Declaring the same period twice changes nothing.
- The multiplier applies to the compensation each session was paid at, so a
  session that started after a promotion is doubled at the promoted rate.
- `get_total_time` and `top_n_workers` are not affected by double pay.

### Examples

The example below shows how this operation should work:

| Query | Explanation |
|---|---|
| `wt = WorkerTimeTracker()` | a tracker with no workers |
| `wt.add_worker("ana", "Developer", 10)` | returns `True` |
| `wt.register("ana", 100)` | returns `True` |
| `wt.register("ana", 200)` | returns `True`; the session `[100, 200)` is paid at 10 |
| `wt.promote("ana", "Senior Developer", 20)` | returns `True` |
| `wt.register("ana", 300)` | returns `True`; the promotion takes effect |
| `wt.register("ana", 400)` | returns `True`; the session `[300, 400)` is paid at 20 |
| `wt.calc_salary("ana", 0, 500)` | returns `3000`; no double pay yet |
| `wt.set_double_pay(350, 450)` | declares the period `[350, 450)` |
| `wt.calc_salary("ana", 0, 500)` | returns `4000`; 100 × 10, then 50 × 20 for `[300, 350)` and 50 × 40 for `[350, 400)` |
| `wt.set_double_pay(380, 420)` | declares a period inside the previous one |
| `wt.calc_salary("ana", 0, 500)` | returns `4000`; overlapping periods do not stack |
| `wt.set_double_pay(150, 190)` | declares a period during the first session, which is already over |
| `wt.calc_salary("ana", 0, 500)` | returns `4400`; the 40 units in `[150, 190)` now earn an extra 10 each |
| `wt.set_double_pay(170, 250)` | overlaps `[150, 190)`; together they cover `[150, 250)` |
| `wt.calc_salary("ana", 0, 500)` | returns `4500`; the doubled part of the first session is now `[150, 200)` |
| `wt.calc_salary("ana", 160, 360)` | returns `2200`; 40 × 20 for `[160, 200)`, 50 × 20 for `[300, 350)`, and 10 × 40 for `[350, 360)` |
| `wt.get_total_time("ana")` | returns `200`; double pay does not change time in the office |
