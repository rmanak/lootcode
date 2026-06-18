def wordDictionary(operations):
    root = {}
    out = []

    def add(word):
        node = root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True

    def search(word):
        def dfs(node, i):
            if i == len(word):
                return "$" in node
            ch = word[i]
            if ch == ".":
                return any(dfs(child, i + 1)
                           for k, child in node.items() if k != "$")
            return ch in node and dfs(node[ch], i + 1)

        return dfs(root, 0)

    for op in operations:
        if op[0] == "addWord":
            add(op[1])
            out.append(None)
        else:
            out.append(search(op[1]))
    return out
