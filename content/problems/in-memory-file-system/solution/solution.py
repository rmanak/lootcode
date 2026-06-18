def fileSystem(operations):
    root = {"dirs": {}, "files": {}}

    def get_dir(parts, create=False):
        node = root
        for p in parts:
            if p not in node["dirs"]:
                if not create:
                    return None
                node["dirs"][p] = {"dirs": {}, "files": {}}
            node = node["dirs"][p]
        return node

    out = []
    for op in operations:
        cmd = op[0]
        if cmd == "mkdir":
            get_dir([p for p in op[1].split("/") if p], create=True)
            out.append(None)
        elif cmd == "addContentToFile":
            parts = [p for p in op[1].split("/") if p]
            node = get_dir(parts[:-1], create=True)
            node["files"][parts[-1]] = node["files"].get(parts[-1], "") + op[2]
            out.append(None)
        elif cmd == "readContentFromFile":
            parts = [p for p in op[1].split("/") if p]
            out.append(get_dir(parts[:-1])["files"][parts[-1]])
        else:
            parts = [p for p in op[1].split("/") if p]
            if parts:
                parent = get_dir(parts[:-1])
                if parent and parts[-1] in parent["files"]:
                    out.append([parts[-1]])
                    continue
            node = get_dir(parts)
            out.append(sorted(list(node["dirs"].keys()) +
                              list(node["files"].keys())))
    return out
