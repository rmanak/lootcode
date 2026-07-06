"""AST mutation operators (technique T5).

Make small, plausible-wrong edits to the canonical — each simulating a bug a user
might actually write (flipped comparison, off-by-one, swapped ``min``/``max`` or
``+``/``-``, weakened boundary). A candidate input that makes a mutant's output
diverge from the canonical *kills* it; the surviving-mutant set measures where the
suite is still blind.

A mutant that merely raises is still killed (it diverges from the canonical, which
we only ever run on inputs where it returns cleanly), so we don't special-case
exceptions here — see the Q1 reply in the plan doc. We only avoid *emitting*
mutants that fail to compile.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Optional

# Comparison flips: the classic off-by-one / boundary-weakening bugs.
_CMP = {
    ast.Lt: [ast.LtE, ast.Gt],
    ast.LtE: [ast.Lt, ast.GtE],
    ast.Gt: [ast.GtE, ast.Lt],
    ast.GtE: [ast.Gt, ast.LtE],
    ast.Eq: [ast.NotEq],
    ast.NotEq: [ast.Eq],
}
# Arithmetic swaps.
_BIN = {
    ast.Add: [ast.Sub],
    ast.Sub: [ast.Add],
    ast.Mult: [ast.FloorDiv],
    ast.FloorDiv: [ast.Mult],
    ast.Div: [ast.Mult],
    ast.Mod: [ast.FloorDiv],
}
_BOOL = {ast.And: ast.Or, ast.Or: ast.And}
_FUNC_SWAP = {"min": "max", "max": "min"}


@dataclass
class Mutant:
    desc: str      # human-readable ("cmp Lt->LtE @op3")
    code: str      # mutated source


def _dfs(node: ast.AST):
    """Deterministic pre-order over all nodes (stable across identical re-parses)."""
    yield node
    for child in ast.iter_child_nodes(node):
        yield from _dfs(child)


def _alts(node: ast.AST) -> list[tuple[str, object]]:
    """Alternative mutations available at ``node`` (as opaque descriptors)."""
    out: list[tuple[str, object]] = []
    if isinstance(node, ast.Compare):
        for i, op in enumerate(node.ops):
            for alt in _CMP.get(type(op), []):
                out.append(("cmp", (i, alt)))
    elif isinstance(node, ast.BinOp) and type(node.op) in _BIN:
        for alt in _BIN[type(node.op)]:
            out.append(("bin", alt))
    elif isinstance(node, ast.BoolOp) and type(node.op) in _BOOL:
        out.append(("bool", _BOOL[type(node.op)]))
    elif (isinstance(node, ast.Constant) and isinstance(node.value, int)
          and not isinstance(node.value, bool) and abs(node.value) <= 1000):
        for delta in (1, -1):
            out.append(("const", delta))
    elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
          and node.func.id in _FUNC_SWAP):
        out.append(("call", _FUNC_SWAP[node.func.id]))
    return out


def _apply(node: ast.AST, kind: str, arg: object) -> str:
    """Mutate ``node`` in place; return a short description."""
    if kind == "cmp":
        i, alt = arg  # type: ignore[misc]
        old = type(node.ops[i]).__name__  # type: ignore[attr-defined]
        node.ops[i] = alt()               # type: ignore[attr-defined]
        return f"cmp {old}->{alt.__name__}@{i}"
    if kind == "bin":
        old = type(node.op).__name__      # type: ignore[attr-defined]
        node.op = arg()                   # type: ignore[operator]
        return f"bin {old}->{arg.__name__}"  # type: ignore[attr-defined]
    if kind == "bool":
        old = type(node.op).__name__      # type: ignore[attr-defined]
        node.op = arg()                   # type: ignore[operator]
        return f"bool {old}->{arg.__name__}"  # type: ignore[attr-defined]
    if kind == "const":
        old = node.value                  # type: ignore[attr-defined]
        node.value = old + arg            # type: ignore[operator]
        return f"const {old}->{node.value}"  # type: ignore[attr-defined]
    if kind == "call":
        old = node.func.id                # type: ignore[attr-defined]
        node.func.id = arg                # type: ignore[assignment]
        return f"call {old}->{arg}"
    return "?"


class _Deleter(ast.NodeTransformer):
    """Neutralize the ``target``-th statement (replace it with ``pass``).

    Statement deletion (SDL) models the highest-value real-bug class our single-
    token operators miss: *missing logic* — a dropped rebalance / update / branch,
    the shape of the median ``sol.py`` bug. Replacing with ``pass`` (rather than
    truly removing) keeps every body non-empty, so the mutant always parses.
    """

    def __init__(self, target: int) -> None:
        self.target = target
        self.i = -1

    # Deleting these produces a broken/empty solution (no function, missing import)
    # rather than a plausible bug, so we never neutralize them.
    _SKIP = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
             ast.Import, ast.ImportFrom)

    def visit(self, node):
        if isinstance(node, ast.stmt) and not isinstance(node, self._SKIP):
            self.i += 1
            if self.i == self.target:
                return ast.copy_location(ast.Pass(), node)
        return super().visit(node)


def _count_stmts(source: str) -> int:
    d = _Deleter(-1)
    d.visit(ast.parse(source))
    return d.i + 1


def _sdl_mutant(source: str, target: int) -> Optional[tuple[str, str]]:
    tree = _Deleter(target).visit(ast.parse(source))
    ast.fix_missing_locations(tree)
    try:
        code = ast.unparse(tree)
        compile(code, "<mutant>", "exec")
    except (SyntaxError, ValueError):
        return None
    return (f"del-stmt@{target}", code)


def make_mutants(source: str, cap: int = 60, seed: int = 0) -> list[Mutant]:
    """Enumerate mutants of ``source`` (single-token edits + statement deletion).

    Capped and sampled deterministically. A mutant that only raises is fine — it
    still diverges from the canonical and gets killed downstream.
    """
    try:
        base = ast.parse(source)
    except SyntaxError:
        return []

    # Single-token edit sites, indexed by pre-order position so each can be
    # re-applied to a fresh parse (parsing is deterministic → index N is stable).
    sites: list[tuple[int, str, object]] = []
    for idx, node in enumerate(_dfs(base)):
        for kind, arg in _alts(node):
            sites.append((idx, kind, arg))

    import random
    rng = random.Random(seed)
    rng.shuffle(sites)

    mutants: list[Mutant] = []
    seen: set[str] = set()

    # Statement-deletion mutants first — they model the missing-logic bug class
    # our token edits can't reach, and are cheap and few.
    sdl_targets = list(range(_count_stmts(source)))
    rng.shuffle(sdl_targets)
    for t in sdl_targets:
        if len(mutants) >= cap // 2:
            break
        out = _sdl_mutant(source, t)
        if not out:
            continue
        desc, code = out
        if code == source or code in seen:
            continue
        seen.add(code)
        mutants.append(Mutant(desc=desc, code=code))

    for idx, kind, arg in sites:
        if len(mutants) >= cap:
            break
        tree = ast.parse(source)
        node = _nth(tree, idx)
        if node is None:
            continue
        desc = _apply(node, kind, arg)
        ast.fix_missing_locations(tree)
        try:
            code = ast.unparse(tree)
            compile(code, "<mutant>", "exec")
        except (SyntaxError, ValueError):
            continue
        if code == source or code in seen:
            continue  # identical (equivalent) mutant — no discriminating value
        seen.add(code)
        mutants.append(Mutant(desc=desc, code=code))
    return mutants


def _nth(tree: ast.AST, idx: int) -> Optional[ast.AST]:
    for i, node in enumerate(_dfs(tree)):
        if i == idx:
            return node
    return None
