#!/usr/bin/env python3
"""numpy ⇄ PyTorch twins: scaffold a twin and keep the two sharing one test suite.

A twin is ``<numpy-slug>-pytorch``: the same exercise as a numpy ML problem on
the PyTorch runtime, kept as close to the original as possible (same names,
shapes, constraints, validator, tests). See docs/pytorch-twins.md.

    scaffold <numpy-slug>   create content/problems/<slug>-pytorch/ from the numpy
                            problem (meta, statement copy, starter, validator,
                            collection entry). The canonical and the statement's
                            framework paragraph are then written by hand.
    port <numpy-slug>       numpy cases -> the twin's cases (expected: null), and
                            the numpy tests/generator.json -> the twin's torch block.
    check <numpy-slug>      cross-check the two canonicals: the twin's (float32,
                            in the torch sandbox) against the numpy one (float64,
                            on the same float32-rounded input), over every stored
                            case plus -n generator draws. Fails above --max-score
                            (in units of the twin's tolerance).
    bake <numpy-slug>       draw -n inputs from the numpy tests/generator.json,
                            keep the -k whose answers differ most, and store them
                            as hidden numpy cases with the numpy canonical's
                            answers (gen-<seed>-<i>; a re-bake replaces them).
                            Works for any numpy problem with a generator, twin
                            or not.

port / bake / scaffold only print what they would do unless --write is given.
Every write is to content files; run seed / verify_bank / audit /
check_constraint_validators afterwards (or ``make check``).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import content  # noqa: E402
from app.config import settings  # noqa: E402
from app.executor import run_submission  # noqa: E402
from app.executor.torch_runtime import unavailable_reason  # noqa: E402
from app.executor.torch_runtime.inputs import generated_inputs, to_plain  # noqa: E402
from authoring import twins  # noqa: E402

#: Tests per sandbox run are bounded by how many numbers they carry, so a run's
#: answers stay inside the ~1 MB result budget (docs/code-execution.md) and its
#: inputs inside the torch runtime's per-run budget.
CHUNK_TESTS = 25
CHUNK_NUMBERS = 15_000
COLLECTION = ROOT / "content" / "collections" / "ml-coding-pytorch.json"
NUMPY_COLLECTION = ROOT / "content" / "collections" / "ml-coding.json"


# --- helpers -------------------------------------------------------------------
def _dir(slug: str) -> pathlib.Path:
    for root in settings.content_dirs:
        if (root / slug / "meta.json").exists():
            return root / slug
    sys.exit(f"ERROR: no problem {slug!r} in any content root")


def _read_json(p: pathlib.Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(p: pathlib.Path, data: dict) -> None:
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _validator(problem_dir: pathlib.Path):
    path = problem_dir / "input_validator" / "input_validator.py"
    spec = importlib.util.spec_from_file_location(f"_v_{problem_dir.name}", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.validate_input


def _outputs(code: str, prob: dict, inputs: list[tuple[str, dict]]) -> dict[str, object]:
    """Run ``code`` for ``prob`` on named inputs; name -> returned value
    (``Exception`` text for a test that did not return)."""
    out: dict[str, object] = {}
    chunks: list[list[tuple[str, dict]]] = [[]]
    size = 0
    for item in inputs:
        n = len(twins.numbers(item[1]))
        if chunks[-1] and (len(chunks[-1]) >= CHUNK_TESTS or size + n > CHUNK_NUMBERS):
            chunks.append([])
            size = 0
        chunks[-1].append(item)
        size += n
    for chunk in chunks:
        tests = [{"name": n, "input": inp, "expected": None, "hidden": True}
                 for n, inp in chunk]
        if not tests:
            continue
        g = run_submission(code, prob, tests)
        for r in g.results:
            if r.name in out or not any(r.name == t["name"] for t in tests):
                continue  # the torch grader's own random-k tests
            out[r.name] = (r.returned if r.status in ("passed", "wrong")
                           else RuntimeError(f"{r.status}: {(r.error or '')[-300:]}"))
    return out


def _pair(numpy_slug: str) -> tuple[pathlib.Path, pathlib.Path]:
    np_dir = _dir(numpy_slug)
    tw_dir = np_dir.parent / twins.twin_slug(numpy_slug)
    if not (tw_dir / "meta.json").exists():
        sys.exit(f"ERROR: {numpy_slug} has no twin yet (scaffold it first)")
    return np_dir, tw_dir


# --- scaffold ------------------------------------------------------------------
_TWIN_TORCH_KEYS = ("twin", "rtol", "atol", "random_tests", "forbid", "dims", "inputs")


def cmd_scaffold(a: argparse.Namespace) -> int:
    np_dir = _dir(a.slug)
    meta = _read_json(np_dir / "meta.json")
    if meta.get("runtime") == "torch":
        sys.exit("ERROR: that is already a torch problem")
    if meta.get("kind") == "class":
        sys.exit("ERROR: class problems cannot take $random inputs yet "
                 "(docs/torch-runtime.md, 'Not yet'); scaffold a function problem")
    tw = twins.twin_slug(a.slug)
    tw_dir = np_dir.parent / tw
    if tw_dir.exists():
        sys.exit(f"ERROR: {tw_dir} already exists")
    fn = meta["function"]
    params = [{**p, "type": twins.twin_param_type(p["type"])} for p in fn["params"]]
    ret = twins.twin_return_type(fn["returns"]["type"])
    gen = twins.load_generator(np_dir)
    tmeta = {
        "slug": tw,
        "title": f"{meta['title']} (PyTorch)",
        "difficulty": meta["difficulty"],
        "tags": [*meta["tags"], "pytorch"],
        **({"hints": meta["hints"]} if meta.get("hints") else {}),
        "languages": ["python"],
        "limits": {"timeLimitMs": max(5000, meta["limits"]["timeLimitMs"]),
                   "memoryLimitMb": 2048},
        "function": {"name": fn["name"], "params": params, "returns": {"type": ret}},
        "scoring": meta.get("scoring", {"type": "weighted", "points": 100}),
        "compare": "close",
        "runtime": "torch",
        "torch": {"twin": a.slug, "rtol": 1e-5, "atol": 1e-6,
                  "random_tests": 5 if gen else 0,
                  "forbid": list(twins.AUTOGRAD) if a.autograd_forbidden else [],
                  **(gen or {})},
    }
    print(f"twin {tw}: {fn['name']}("
          + ", ".join(f"{p['name']}: {p['type']}" for p in params) + f") -> {ret}")
    if not gen:
        print("  note: the numpy problem has no tests/generator.json yet, so the twin "
              "gets no random tests until one is written and `port` is re-run")
    if not a.write:
        print("(dry run; --write to create it)")
        return 0
    (tw_dir / "tests").mkdir(parents=True)
    (tw_dir / "solution").mkdir()
    (tw_dir / "starters" / "python").mkdir(parents=True)
    (tw_dir / "input_validator").mkdir()
    _write_json(tw_dir / "meta.json", tmeta)
    md, replaced = twins.twin_statement(
        (np_dir / "problem.md").read_text(encoding="utf-8"),
        twins.torch_paragraph(fn["params"], params, ret, tmeta["torch"]))
    (tw_dir / "problem.md").write_text(md, encoding="utf-8")
    if not replaced:
        print("  note: no 'You may use **numpy**' paragraph found; write the "
              "framework paragraph into problem.md by hand")
    if (np_dir / "assets").is_dir():
        shutil.copytree(np_dir / "assets", tw_dir / "assets")
    shutil.copy(np_dir / "input_validator" / "input_validator.py",
                tw_dir / "input_validator" / "input_validator.py")
    sig = ", ".join(p["name"] for p in params)
    (tw_dir / "starters" / "python" / "solution.py").write_text(
        f"import torch\n\n\ndef {fn['name']}({sig}):\n    pass\n", encoding="utf-8")
    (tw_dir / "solution" / "solution.py").write_text(
        f"import torch\n\n\ndef {fn['name']}({sig}):\n"
        "    raise NotImplementedError('write the reference solution')\n", encoding="utf-8")
    _write_json(tw_dir / "tests" / "cases.json", {"cases": []})
    _add_to_collection(a.slug, tw)
    print(f"created {tw_dir.relative_to(ROOT)}; next: write solution/solution.py, "
          "adapt problem.md's framework paragraph, then `port --write` and `check`")
    return 0


def _add_to_collection(numpy_slug: str, tw: str) -> None:
    coll = _read_json(COLLECTION)
    if tw in coll["problems"]:
        return
    order = _read_json(NUMPY_COLLECTION)["problems"]
    rank = {s + twins.TWIN_SUFFIX: i for i, s in enumerate(order)}
    coll["problems"].append(tw)
    # Twins in the numpy study order; anything else (a torch-only problem) first.
    coll["problems"].sort(key=lambda s: rank.get(s, -1))
    _write_json(COLLECTION, coll)


# --- port ----------------------------------------------------------------------
def cmd_port(a: argparse.Namespace) -> int:
    np_dir, tw_dir = _pair(a.slug)
    np_meta, tw_meta = _read_json(np_dir / "meta.json"), _read_json(tw_dir / "meta.json")
    gen = twins.load_generator(np_dir)
    np_params = np_meta["function"]["params"]
    tw_params = tw_meta["function"]["params"]
    np_cases = _read_json(np_dir / "tests" / "cases.json")["cases"]
    tw_cases = _read_json(tw_dir / "tests" / "cases.json")["cases"]
    new = twins.port_cases(np_cases, np_params, tw_params, gen, tw_cases)

    valid = _validator(tw_dir)
    bad = [c["name"] for c in new
           if not valid(**twins.concrete_twin_input(c["input"], tw_params, c["name"]))]
    if bad:
        print(f"ERROR: the twin's validator rejects {bad}; the twin's constraints "
              "must be the numpy problem's (docs/pytorch-twins.md)")
        return 1

    torch_block = dict(tw_meta.get("torch") or {})
    if gen:
        torch_block["dims"], torch_block["inputs"] = gen["dims"], gen["inputs"]
        torch_block.setdefault("random_tests", 5)
    changed_meta = torch_block != tw_meta.get("torch")
    changed_cases = new != tw_cases
    print(f"{tw_dir.name}: {len(new)} cases ({len(np_cases)} from {a.slug}), "
          f"cases {'change' if changed_cases else 'unchanged'}, generator "
          f"{'changes' if changed_meta else 'unchanged' if gen else 'absent'}")
    if not a.write:
        print("(dry run; --write to apply)")
        return 0
    if changed_cases:
        _write_json(tw_dir / "tests" / "cases.json", {"cases": new})
    if changed_meta:
        # Rebuild in a stable key order, so a re-port is a no-op diff.
        tw_meta["torch"] = {k: torch_block[k] for k in _TWIN_TORCH_KEYS if k in torch_block}
        tw_meta["torch"].update({k: v for k, v in torch_block.items()
                                 if k not in _TWIN_TORCH_KEYS})
        _write_json(tw_dir / "meta.json", tw_meta)
    return 0


# --- check ---------------------------------------------------------------------
def cmd_check(a: argparse.Namespace) -> int:
    reason = unavailable_reason()
    if reason:
        print(f"SKIP: the PyTorch runtime is not available ({reason})")
        return 0
    np_dir, tw_dir = _pair(a.slug)
    np_prob, tw_prob = content.load_problem_dir(np_dir), content.load_problem_dir(tw_dir)
    cfg = tw_prob["runtime_config"] or {}
    rtol, atol = float(cfg.get("rtol", 1e-5)), float(cfg.get("atol", 1e-6))
    tw_params = tw_prob["params"]
    # No fresh random tests in these runs: we bring our own draws, by name.
    tw_prob["runtime_config"] = {**cfg, "random_tests": 0}

    torch_in: list[tuple[str, dict]] = []
    numpy_in: list[tuple[str, dict]] = []
    for c in tw_prob["tests"]:
        torch_in.append((c["name"], c["input"]))
        numpy_in.append((c["name"], twins.round_like_torch(
            twins.concrete_twin_input(c["input"], tw_params, c["name"]), cfg, tw_params)))
    if cfg.get("inputs") and a.n:
        for i, inp in enumerate(generated_inputs(cfg, tw_params, seed=a.seed, count=a.n)):
            name = f"draw-{i + 1}"
            torch_in.append((name, inp))
            numpy_in.append((name, twins.round_like_torch(to_plain(inp), cfg, tw_params)))

    t_out = _outputs(tw_prob["canonical_solution"], tw_prob, torch_in)
    n_out = _outputs(np_prob["canonical_solution"], np_prob, numpy_in)
    worst, rows, failed = 0.0, [], 0
    for name, _ in torch_in:
        t, n = t_out.get(name), n_out.get(name)
        if isinstance(t, Exception) or isinstance(n, Exception) or name not in t_out:
            failed += 1
            rows.append((math.inf, name, f"torch: {t}; numpy: {n}"))
            continue
        score, where = twins.disagreement(t, n, rtol, atol)
        rows.append((score, name, where))
        worst = max(worst, score)
    rows.sort(key=lambda r: -r[0])
    stored = len(tw_prob["tests"])
    print(f"{tw_dir.name} vs {a.slug}: {stored} stored + {len(torch_in) - stored} drawn "
          f"inputs; worst disagreement {worst:.3g} x tolerance (rtol={rtol:g}, "
          f"atol={atol:g}; limit {a.max_score:g})")
    for score, name, where in rows[: (len(rows) if a.verbose else 5)]:
        print(f"  {score:9.3g}  {name:32}  {where}")
    if failed:
        print(f"FAIL: {failed} input(s) where a canonical did not return")
        return 1
    if worst > a.max_score:
        print("FAIL: the canonicals disagree past the limit: a contract mismatch "
              "(mean vs sum, a tie rule, biased vs unbiased) or an ill-conditioned "
              "input the generator should not produce")
        return 1
    print("OK")
    return 0


# --- bake ----------------------------------------------------------------------
def _has_float(v: object) -> bool:
    if isinstance(v, float):
        return True
    if isinstance(v, list):
        return any(_has_float(x) for x in v)
    if isinstance(v, dict):
        return any(_has_float(x) for x in v.values())
    return False


def _finite(v: object) -> bool:
    return all(math.isfinite(x) for x in twins.numbers(v))


def cmd_bake(a: argparse.Namespace) -> int:
    np_dir = _dir(a.slug)
    prob = content.load_problem_dir(np_dir)
    if prob["runtime"] != "python":
        sys.exit("ERROR: bake stores expected values; a torch problem's canonical is "
                 "its oracle. Bake the numpy sibling and `port` it instead.")
    gen = twins.load_generator(np_dir)
    if not gen:
        sys.exit(f"ERROR: {np_dir.relative_to(ROOT)}/tests/generator.json does not exist")
    draws = twins.draw_inputs(gen, prob["params"], seed=a.seed, count=a.n)
    valid = _validator(np_dir)
    legal = [d for d in draws if valid(**d)]
    if len(legal) < len(draws):
        print(f"ERROR: {len(draws) - len(legal)} of {len(draws)} draws break the "
              "validator. The twin draws from the same generator on every run, so it "
              "must only produce legal inputs; fix tests/generator.json.")
        return 1
    named = [(f"draw-{i + 1}", d) for i, d in enumerate(legal)]
    outs = _outputs(prob["canonical_solution"], prob, named)
    ok = [(d, outs[n]) for n, d in named
          if n in outs and not isinstance(outs[n], Exception) and _finite(outs[n])]
    if len(ok) < len(named):
        print(f"  note: {len(named) - len(ok)} draw(s) skipped (the canonical errored or "
              "returned a non-finite value)")
    if prob["compare"] != "close" and any(_has_float(o) for _, o in ok) and not a.force:
        print(f"ERROR: compare is {prob['compare']!r} and the answers hold floats, which "
              "would be compared bit for bit; use --force if they are exact")
        return 1
    picks, size = [], 0
    for i in twins.stratify(ok, len(ok)):  # every draw, most-different first
        kb = len(json.dumps([ok[i][0], ok[i][1]])) / 1024
        if size + kb <= a.max_kb:
            picks.append(i)
            size += kb
        if len(picks) == a.k:
            break
    picks.sort()
    cases_path = np_dir / "tests" / "cases.json"
    cases = _read_json(cases_path)["cases"]
    kept = [c for c in cases if not c["name"].startswith("gen-")]
    baked = [{"name": f"gen-{a.seed}-{j + 1}", "input": ok[i][0], "expected": ok[i][1],
              "weight": 1, "hidden": True} for j, i in enumerate(picks)]
    size = len(json.dumps(baked))
    print(f"{a.slug}: {len(ok)} answered draws, keeping {len(baked)} "
          f"({size / 1024:.0f} KB), replacing {len(cases) - len(kept)} earlier gen-* cases")
    for c in baked:
        nums = twins.numbers(c["expected"])
        print(f"  {c['name']:14} answer: {len(nums)} numbers in "
              f"[{min(nums, default=0):.4g}, {max(nums, default=0):.4g}]")
    if not a.write:
        print("(dry run; --write to apply)")
        return 0
    _write_json(cases_path, {"cases": kept + baked})
    if (np_dir.parent / twins.twin_slug(a.slug)).exists():
        print(f"  the twin exists: run `port {a.slug} --write` so it gets these cases too")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("scaffold")
    p.add_argument("slug")
    p.add_argument("--autograd-forbidden", action="store_true",
                   help="a hand-written-gradient problem: forbid torch autograd")
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("port")
    p.add_argument("slug")
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("check")
    p.add_argument("slug")
    p.add_argument("-n", type=int, default=200, help="generator draws (default 200)")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--max-score", type=float, default=0.5)
    p.add_argument("-v", "--verbose", action="store_true")
    p = sub.add_parser("bake")
    p.add_argument("slug")
    p.add_argument("-n", type=int, default=300, help="draws to choose from (default 300)")
    p.add_argument("-k", type=int, default=6, help="cases to keep (default 6)")
    p.add_argument("--max-kb", type=float, default=60,
                   help="size budget for the kept cases (default 60 KB)")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--force", action="store_true")
    p.add_argument("--write", action="store_true")
    a = ap.parse_args()
    return {"scaffold": cmd_scaffold, "port": cmd_port, "check": cmd_check,
            "bake": cmd_bake}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
