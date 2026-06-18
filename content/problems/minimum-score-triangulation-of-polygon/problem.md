A convex polygon has vertices labelled `values[0..N-1]` in order. Triangulate it
into `N - 2` triangles; each triangle's value is the product of its three vertex
labels, and the total score is the sum over all triangles. **Return the minimum
possible total score.**

**Examples**
```
values = [1,2,3]      ->  6
values = [3,7,4,5]     ->  144
values = [1,3,1,4,1,5] ->  13
```

**Constraints:** `3 <= len(values) <= 50`, `1 <= values[i] <= 100`.
