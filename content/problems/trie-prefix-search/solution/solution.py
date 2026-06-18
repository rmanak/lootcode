def trieOps(operations):
    root, out = {}, []
    for op in operations:
        name, s = op[0], op[1]
        if name == "insert":
            node = root
            for ch in s:
                node = node.setdefault(ch, {})
            node["$"] = True
            out.append(None)
        else:
            node, ok = root, True
            for ch in s:
                if ch not in node:
                    ok = False
                    break
                node = node[ch]
            out.append((ok and "$" in node) if name == "search" else ok)
    return out
