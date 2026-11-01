"""Input-constraint validator for problem 'autograd-on-a-graph'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound:
- 1..500 nodes with unique non-empty string ids (at most 20 chars);
- each node has exactly the keys its op needs: "input"/"const" carry a
  finite "value" with |value| <= 100 and no inputs; binary ops (add, sub,
  mul, div) carry 2 inputs; unary ops (neg, exp, log, tanh, sigmoid, relu)
  1 input; "pow" 1 input plus a finite "exponent" with |exponent| <= 10;
- every input names an existing node; the graph is acyclic and no path is
  longer than 500 nodes;
- output names an existing node;
- domain rules hold when evaluated: no division by 0, log only of positive
  values, pow of a negative base only with an integer exponent and of 0 only
  with exponent 0 or >= 1, exp/sigmoid/tanh inputs within [-100, 100],
  every value finite with |value| <= 1e12.

Not checked here: the gradient-size promise (every gradient finite with
|grad| <= 1e12) and the relu promise (a relu input is exactly 0 or at least
1e-6 from it). The case generator vets both.
"""
import math

_ARITY = {"add": 2, "sub": 2, "mul": 2, "div": 2, "neg": 1, "exp": 1, "log": 1, "tanh": 1, "sigmoid": 1,
          "relu": 1, "pow": 1}


def _num(v, lim):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= lim


def validate_input(nodes, output):
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 500:
        return False
    by_id = {}
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or not 1 <= len(n["id"]) <= 20:
            return False
        if n["id"] in by_id:
            return False
        by_id[n["id"]] = n
    for n in nodes:
        op = n.get("op")
        if op in ("input", "const"):
            if set(n) != {"id", "op", "value"} or not _num(n["value"], 100):
                return False
        elif op in _ARITY:
            want = {"id", "op", "inputs"} | ({"exponent"} if op == "pow" else set())
            if set(n) != want or not isinstance(n["inputs"], list) or len(n["inputs"]) != _ARITY[op]:
                return False
            if not all(isinstance(s, str) and s in by_id for s in n["inputs"]):
                return False
            if op == "pow" and not _num(n["exponent"], 10):
                return False
        else:
            return False
    if not isinstance(output, str) or output not in by_id:
        return False
    # Acyclic + longest path, by memoized depth with an explicit stack.
    depth, state = {}, {}
    for start in by_id:
        stack = [(start, 0)]
        while stack:
            nid, i = stack.pop()
            srcs = by_id[nid].get("inputs", [])
            if i == 0:
                if state.get(nid) == "done":
                    continue
                if state.get(nid) == "open":
                    return False                     # a cycle
                state[nid] = "open"
            if i < len(srcs):
                stack.append((nid, i + 1))
                s = srcs[i]
                if state.get(s) == "open":
                    return False
                if state.get(s) != "done":
                    stack.append((s, 0))
            else:
                state[nid] = "done"
                depth[nid] = 1 + max((depth[s] for s in srcs), default=0)
                if depth[nid] > 500:
                    return False
    # Evaluate with the domain rules.
    order = sorted(by_id, key=lambda k: depth[k])
    val = {}
    for nid in order:
        n = by_id[nid]; op = n["op"]; xs = [val[s] for s in n.get("inputs", [])]
        try:
            if op in ("input", "const"):
                v = float(n["value"])
            elif op == "add":
                v = xs[0] + xs[1]
            elif op == "sub":
                v = xs[0] - xs[1]
            elif op == "mul":
                v = xs[0] * xs[1]
            elif op == "div":
                if xs[1] == 0:
                    return False
                v = xs[0] / xs[1]
            elif op == "neg":
                v = -xs[0]
            elif op == "pow":
                p = n["exponent"]
                if (xs[0] < 0 and float(p) != int(p)) or (xs[0] == 0 and p != 0 and p < 1):
                    return False
                v = xs[0] ** p
            elif op == "log":
                if xs[0] <= 0:
                    return False
                v = math.log(xs[0])
            elif op in ("exp", "sigmoid", "tanh"):
                if abs(xs[0]) > 100:
                    return False
                v = math.exp(xs[0]) if op == "exp" else (math.tanh(xs[0]) if op == "tanh"
                                                         else 1 / (1 + math.exp(-xs[0])))
            else:
                v = max(xs[0], 0.0)
        except (OverflowError, ZeroDivisionError, ValueError):
            return False
        if not isinstance(v, float) or not math.isfinite(v) or abs(v) > 1e12:
            return False
        val[nid] = v
    return True
