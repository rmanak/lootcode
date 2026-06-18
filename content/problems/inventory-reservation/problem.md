`stock` maps each SKU to its available quantity. Process each request `[sku, qty]` in
order: accept it (returning `true`) only if the remaining quantity for that SKU is at
least `qty`, decrementing the remaining stock; otherwise reject it (`false`). A
missing SKU has zero stock. Return the accept/reject result for each request.

## Constraints
- `0 <= len(requests) <= 2*10^5`
- quantities are non-negative and fit in a signed 64-bit integer

## Examples
Input: `stock = {"A":5}, requests = [["A",3],["A",3],["A",2]]`
Output: `[true,false,true]`
Explanation: After accepting 3, only 2 remain, so the next request for 3 fails; the
final request for 2 fits exactly.

Input: `stock = {}, requests = [["B",1]]`
Output: `[false]`
Explanation: `B` has no stock, so the request is rejected.
