#!/usr/bin/env python3
"""Find duplicate problems by *behavior* alone — no words involved.

The generalized form of Stage 2 in ``docs/duplicate-detection-plan.md``. Group
every problem by its call signature (kind + parameter types + return type), pool
the group's own stored test inputs into one shared battery, and run each
problem's canonical solution over that battery. Two problems whose canonicals
return the same vector of answers on the same inputs compute the same function —
which catches duplicates that share no vocabulary at all (climbing stairs ↔
compositions of {1,2}), where every lexical heuristic is blind.

Inputs are borrowed from sibling problems in the same signature group, so they
are realistic rather than random; a canonical that rejects one (out of its
declared constraints) just records an error marker, and error markers only count
as agreement when both sides also agree on real answers.

A fingerprint is only trusted when the problem answered at least ``--min-answers``
battery inputs and produced more than one distinct answer (a function that
returns 0 for everything agrees with every other such function and means
nothing).

Rich-typed problems (TreeNode / ListNode / DoublyLinkedList) are skipped: their
stored JSON needs the harness codecs to become real objects.

Usage:
    python scripts/behavioral_duplicate_scan.py -o behavioral.json
    python scripts/behavioral_duplicate_scan.py --battery 16 -j 12
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from app import content  # noqa: E402

ROOTS = [REPO_ROOT / "content" / "problems",
         REPO_ROOT / "content" / "problems-extended"]

RICH_TYPES = {"TreeNode", "ListNode", "DoublyLinkedList"}

PROBE = r'''
import json, signal, sys

sys.setrecursionlimit(20000)
payload = json.loads(sys.stdin.read())
ns = {}
try:
    exec(payload["code"], ns)
except Exception as exc:
    print(json.dumps({"error": "load: %s" % exc}))
    raise SystemExit(0)
fn = ns.get(payload["fn"])
if fn is None:
    print(json.dumps({"error": "no function %s" % payload["fn"]}))
    raise SystemExit(0)


class _T(Exception):
    pass


def _alarm(sig, frm):
    raise _T()


signal.signal(signal.SIGALRM, _alarm)
out = []
for args in payload["battery"]:
    signal.setitimer(signal.ITIMER_REAL, payload["per_case_timeout"])
    try:
        out.append(["ok", fn(*args)])
    except _T:
        out.append(["timeout", None])
    except Exception as exc:
        out.append(["err", type(exc).__name__])
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
print(json.dumps(out, default=str))
'''


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def load_bank() -> list[dict]:
    out = []
    for root in ROOTS:
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            if not d.is_dir() or not (d / "meta.json").is_file():
                continue
            try:
                p = content.load_problem_dir(d)
            except Exception:  # noqa: S112 - a malformed dir is skipped, not fatal
                continue
            p["_root"] = root.name
            out.append(p)
    return out


def signature(p: dict) -> tuple | None:
    if p.get("kind") != "function":
        return None
    types = tuple((q.get("type") or "") for q in (p.get("params") or []))
    ret = p.get("return_type") or ""
    if not types or any(t in RICH_TYPES for t in types) or ret in RICH_TYPES:
        return None
    return (types, ret)


def positional(p: dict, test_input) -> list | None:
    """A test's input dict re-expressed as positional args in declared order."""
    names = [q.get("name") for q in (p.get("params") or [])]
    if isinstance(test_input, dict):
        if any(n not in test_input for n in names):
            return None
        return [test_input[n] for n in names]
    if isinstance(test_input, list) and len(test_input) == len(names):
        return list(test_input)
    return None


def build_battery(group: list[dict], size: int) -> list[list]:
    """Deterministic sample of the group's own test inputs, positionalized."""
    pool: dict[str, list] = {}
    for p in group:
        for t in p.get("tests") or []:
            args = positional(p, t.get("input"))
            if args is None:
                continue
            key = canon(args)
            if len(key) < 4000:            # skip giant inputs; they only slow us
                pool.setdefault(key, args)
    keys = sorted(pool, key=lambda k: hashlib.sha256(k.encode()).hexdigest())
    return [pool[k] for k in keys[:size]]


def probe(p: dict, battery: list[list], per_case_timeout: float,
          total_timeout: float) -> list | None:
    code = p.get("canonical_solution") or ""
    if not code.strip():
        return None
    payload = json.dumps({"code": code, "fn": p["function_name"],
                          "battery": battery,
                          "per_case_timeout": per_case_timeout})
    try:
        r = subprocess.run([sys.executable, "-c", PROBE], input=payload,
                           capture_output=True, text=True, timeout=total_timeout)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    try:
        res = json.loads(r.stdout.splitlines()[-1])
    except Exception:
        return None
    if isinstance(res, dict):        # load error
        return None
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", type=pathlib.Path,
                    default=REPO_ROOT / "behavioral_duplicates.json")
    ap.add_argument("--battery", type=int, default=14)
    ap.add_argument("--min-answers", type=int, default=4,
                    help="battery inputs a problem must actually answer (default 4)")
    ap.add_argument("--min-agreement", type=float, default=0.85)
    ap.add_argument("-j", "--jobs", type=int, default=10)
    ap.add_argument("--per-case-timeout", type=float, default=2.0)
    args = ap.parse_args()

    bank = load_bank()
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for p in bank:
        sig = signature(p)
        if sig is not None:
            groups[sig].append(p)
    groups = {k: v for k, v in groups.items() if len(v) > 1}
    n_probl = sum(len(v) for v in groups.values())
    print(f"{len(groups)} signature groups covering {n_probl} problems",
          file=sys.stderr)

    jobs = []
    for sig, group in groups.items():
        battery = build_battery(group, args.battery)
        if len(battery) < args.min_answers:
            continue
        for p in group:
            jobs.append((sig, p, battery))

    answers: dict[str, tuple] = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futs = {pool.submit(probe, p, battery, args.per_case_timeout,
                            args.per_case_timeout * len(battery) + 15): (sig, p)
                for sig, p, battery in jobs}
        done = 0
        for fut in as_completed(futs):
            sig, p = futs[fut]
            res = fut.result()
            done += 1
            if done % 100 == 0:
                print(f"  probed {done}/{len(jobs)}", file=sys.stderr)
            if res is None:
                continue
            answers[p["slug"]] = (sig, res)

    print(f"usable fingerprints: {len(answers)}", file=sys.stderr)

    by_sig: dict[tuple, list[str]] = defaultdict(list)
    for slug, (sig, _res) in answers.items():
        by_sig[sig].append(slug)

    pairs = []
    for sig, slugs in by_sig.items():
        for i in range(len(slugs)):
            for j in range(i + 1, len(slugs)):
                a, b = slugs[i], slugs[j]
                ra, rb = answers[a][1], answers[b][1]
                n = min(len(ra), len(rb))
                real = agree = 0
                distinct = set()
                for k in range(n):
                    sa, va = ra[k]
                    sb, vb = rb[k]
                    if sa != "ok" or sb != "ok":
                        continue
                    real += 1
                    if canon(va) == canon(vb):
                        agree += 1
                        distinct.add(canon(va))
                if real < args.min_answers or len(distinct) < 2:
                    continue
                frac = agree / real
                if frac >= args.min_agreement:
                    pairs.append({
                        "a": a, "b": b, "agreement": round(frac, 3),
                        "agreed": agree, "compared": real,
                        "distinct_answers": len(distinct),
                        "signature": f"{sig[0]} -> {sig[1]}",
                    })

    pairs.sort(key=lambda r: (-r["agreement"], -r["compared"]))
    args.output.write_text(json.dumps(pairs, indent=2))
    print(f"{len(pairs)} behaviorally-agreeing pairs -> {args.output}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
