A supermarket gives a discount to every `n`-th customer. Product `products[i]` has unit
price `prices[i]`. The `c`-th customer (1-indexed) buys, for each `j`,
`order_amounts[c][j]` units of product `order_products[c][j]`. Their bill is the sum of
unit-price times amount; if `c` is a multiple of `n`, the bill becomes
`bill - (discount * bill) / 100`. Return the list of bills, **each rounded to 5
decimal places**.

**Example**
```
n = 3, discount = 50, products = [1,2,3,4,5,6,7],
prices = [100,200,300,400,300,200,100]
order_products = [[1,2],[3,7],[1,2,3,4,5,6,7],[4],[7,3],[7,5,3,1,6,4,2],[2,3,5]]
order_amounts  = [[1,2],[10,10],[1,1,1,1,1,1,1],[10],[10,10],[10,10,10,9,9,9,7],[5,3,2]]
    ->  [500.0,4000.0,800.0,4000.0,4000.0,7350.0,2500.0]
```

**Constraints:** `1 <= n <= 10^4`, `0 <= discount <= 100`, distinct `products`,
`1 <= prices[i] <= 1000`, every ordered product exists, `1 <= amount <= 1000`.
