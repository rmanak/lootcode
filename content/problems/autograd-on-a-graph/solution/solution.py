import math


def _forward(op, xs, node):
    if op in ("input", "const"):
        return float(node["value"])
    if op == "add":
        return xs[0] + xs[1]
    if op == "sub":
        return xs[0] - xs[1]
    if op == "mul":
        return xs[0] * xs[1]
    if op == "div":
        return xs[0] / xs[1]
    if op == "neg":
        return -xs[0]
    if op == "pow":
        return xs[0] ** node["exponent"]
    if op == "exp":
        return math.exp(xs[0])
    if op == "log":
        return math.log(xs[0])
    if op == "tanh":
        return math.tanh(xs[0])
    if op == "sigmoid":
        return 1.0 / (1.0 + math.exp(-xs[0]))
    return xs[0] if xs[0] > 0 else 0.0                     # relu


def _local_grads(op, xs, y, node):
    """d(node) / d(each input), given the inputs xs and the node's own value y."""
    if op == "add":
        return [1.0, 1.0]
    if op == "sub":
        return [1.0, -1.0]
    if op == "mul":
        return [xs[1], xs[0]]
    if op == "div":
        return [1.0 / xs[1], -xs[0] / (xs[1] * xs[1])]
    if op == "neg":
        return [-1.0]
    if op == "pow":
        p = node["exponent"]
        return [0.0 if p == 0 else p * xs[0] ** (p - 1)]   # x ** 0 is the constant 1
    if op == "exp":
        return [y]
    if op == "log":
        return [1.0 / xs[0]]
    if op == "tanh":
        return [1.0 - y * y]
    if op == "sigmoid":
        return [y * (1.0 - y)]
    return [1.0 if xs[0] > 0 else 0.0]                     # relu: derivative 0 at exactly 0


def autogradGraph(nodes, output):
    by_id = {n["id"]: n for n in nodes}

    # Topological order (inputs before users), iteratively, from the given ids.
    order, state = [], {}
    for start in by_id:
        if start in state:
            continue
        stack = [(start, False)]
        while stack:
            nid, expanded = stack.pop()
            if expanded:
                state[nid] = "done"
                order.append(nid)
                continue
            if nid in state:
                continue
            state[nid] = "open"
            stack.append((nid, True))
            for src in by_id[nid].get("inputs", []):
                if src not in state:
                    stack.append((src, False))

    value = {}
    for nid in order:
        node = by_id[nid]
        value[nid] = _forward(node["op"], [value[s] for s in node.get("inputs", [])], node)

    grad = {nid: 0.0 for nid in by_id}
    grad[output] = 1.0
    for nid in reversed(order):                            # every user is processed before its inputs
        node = by_id[nid]
        srcs = node.get("inputs", [])
        if not srcs or grad[nid] == 0.0:
            continue
        local = _local_grads(node["op"], [value[s] for s in srcs], value[nid], node)
        for s, g in zip(srcs, local):
            grad[s] += grad[nid] * g                       # accumulate: a node may feed many users
    return [value[output], [grad[n["id"]] for n in nodes]]
