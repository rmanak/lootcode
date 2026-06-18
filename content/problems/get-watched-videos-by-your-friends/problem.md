There are `n` people with ids `0..n-1`. `watchedVideos[i]` lists the videos watched
by person `i`, and `friends[i]` lists that person's friends (the friendship graph is
undirected). Starting from person `id`, the people at *level k* are exactly those
whose shortest-path distance to you equals `k`.

Collect all videos watched by the people at the given `level`, and return them
ordered by **frequency (increasing)**; videos with equal frequency are ordered
alphabetically.

**Examples**
```
watchedVideos = [["A","B"],["C"],["B","C"],["D"]],
friends = [[1,2],[0,3],[0,3],[1,2]], id = 0, level = 1   ->  ["B","C"]

same graph, level = 2                                    ->  ["D"]
```

**Constraints:** `2 <= n <= 100`, `1 <= level < n`, the graph is undirected.
