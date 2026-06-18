Each entry of `orders` is `[customerName, tableNumber, foodItem]`. Build the
restaurant's display table:

- The first row is a header: `"Table"` followed by every distinct food item in
  **alphabetical order**.
- Each later row starts with a table number and lists how many of each food that
  table ordered, in the same column order as the header.
- Rows are sorted by table number in **numerically increasing** order.

All numbers in the result are returned as strings.

**Example**
```
orders = [["David","3","Ceviche"],["Corina","10","Beef Burrito"],
          ["David","3","Fried Chicken"],["Carla","5","Water"],
          ["Carla","5","Ceviche"],["Rous","3","Ceviche"]]
->  [["Table","Beef Burrito","Ceviche","Fried Chicken","Water"],
     ["3","0","2","1","0"],["5","0","1","0","1"],["10","1","0","0","0"]]
```

**Constraints:** `1 <= len(orders) <= 5*10^4`; table numbers are between `1` and
`500`.
