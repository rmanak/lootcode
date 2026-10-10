#!/usr/bin/env python3
"""Is this problem already in the bank? Look one problem up by URL, slug or title.

The single-query counterpart of ``scripts/find_duplicate_problems.py``, which
compares the bank against itself. Given a LeetCode URL (or bare LeetCode slug)
this fetches the problem from LeetCode's public GraphQL endpoint: title,
difficulty, tags, signature, example inputs and statement. Premium statements,
which LeetCode withholds, come from the doocs/leetcode mirror on GitHub. It then
checks the problem against every content root (default + extended):

  slug     a bank directory is named after the slug             -> in the bank
  title    the normalized titles are equal                       -> in the bank
  example  a stored test case has the same input as an example   -> strong
  fname    same solver function / class name (``hasPathSum``)    -> candidate
  name     IDF-weighted slug+title token overlap                 -> candidate
  stmt     TF-IDF cosine between the two statements              -> candidate

Only ``slug`` and ``title`` are conclusive. Two matching examples, or one plus a
matching function name, read as "likely in the bank". Everything else ranks
candidates for a human (or the ``/add-from-url`` skill) to confirm by reading
the statements. Siblings ("Path Sum" vs "Path Sum II") share most of their
tokens and often their function name, so a high score is evidence, not a
verdict.

Other sites are not fetched. Read the page yourself and pass what you found:
``--title`` (and ``--statement FILE`` for the statement signal).

Usage:
    python scripts/find_problem.py https://leetcode.com/problems/path-sum/
    python scripts/find_problem.py path-sum                    # bare LeetCode slug
    python scripts/find_problem.py https://neetcode.io/problems/x --title "Two Sum"
    python scripts/find_problem.py <url> --save DIR            # also write DIR/<slug>.json

``--save`` writes everything fetched, including a draft Markdown statement
converted from LeetCode's HTML (``statement_md``) and the figure URLs it
references (``images``). The draft still needs the usual import cleanup.

Exit status: 0 = in the bank, 3 = likely in the bank (confirm), 1 = not found,
2 = usage or lookup error.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))  # scripts/ is not a package

from find_duplicate_problems import (  # noqa: E402
    GENERIC_FN_NAMES,
    Problem,
    _canon,
    load_bank,
    statement_tokens,
)

from app.config import settings  # noqa: E402
from app.problem_validation import _stemmed_tokens  # noqa: E402
from app.tags import normalize_tags  # noqa: E402

GRAPHQL = "https://leetcode.com/graphql"
DOOCS = "https://raw.githubusercontent.com/doocs/leetcode/main/solution"
QUERY = """query q($s: String!) { question(titleSlug: $s) {
  questionFrontendId title titleSlug difficulty isPaidOnly categoryTitle
  topicTags { slug } metaData exampleTestcaseList content
  codeSnippets { langSlug code } } }"""
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0 (lootcode find_problem.py)",
}
LEETCODE_HOSTS = {"leetcode.com", "www.leetcode.com", "leetcode.cn"}


def _get(url: str, data: bytes | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers=HEADERS)  # noqa: S310
    with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310
        return resp.read()


def parse_target(arg: str) -> tuple[str, str | None]:
    """``(slug_guess, leetcode_slug)`` for a URL, a bare slug or a title."""
    if "://" not in arg:
        if re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", arg.strip()):
            return arg.strip(), arg.strip()
        return re.sub(r"[^a-z0-9]+", "-", arg.lower()).strip("-"), None
    u = urllib.parse.urlparse(arg)
    parts = [p for p in u.path.split("/") if p]
    if u.netloc.lower() in LEETCODE_HOSTS and "problems" in parts:
        i = parts.index("problems")
        if i + 1 < len(parts):
            return parts[i + 1], parts[i + 1]
    generic = {"problems", "problem", "description", "solutions", "editorial"}
    tail = [p for p in parts if p not in generic]
    return (tail[-1].lower() if tail else ""), None


def fetch_leetcode(slug: str) -> dict | None:
    body = json.dumps({"query": QUERY, "variables": {"s": slug}}).encode()
    q = json.loads(_get(GRAPHQL, body)).get("data", {}).get("question")
    if not q:
        return None
    q["source"] = "leetcode" if q.get("content") else None
    if not q.get("content"):  # premium: LeetCode withholds the statement
        q["content"] = fetch_doocs(int(q["questionFrontendId"]), q["title"])
        q["source"] = "doocs" if q["content"] else None
    return q


def fetch_doocs(qid: int, title: str) -> str | None:
    lo = qid // 100 * 100
    folder = urllib.parse.quote(f"{qid:04d}.{title}")
    url = f"{DOOCS}/{lo:04d}-{lo + 99:04d}/{folder}/README_EN.md"
    try:
        text = _get(url).decode()
    except (urllib.error.URLError, TimeoutError):
        return None
    m = re.search(r"<!-- description:start -->(.*?)<!-- description:end -->",
                  text, re.S)
    return m.group(1).strip() if m else None


def html_to_markdown(src: str) -> str:
    """A rough draft of LeetCode's statement HTML as bank-style Markdown."""
    def pre(m: re.Match) -> str:
        return "\n```\n" + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "\n```\n"

    s = src.replace("\r", "")
    s = re.sub(r"<pre>(.*?)</pre>", pre, s, flags=re.S)
    s = re.sub(r"<img[^>]*?src=\"([^\"]+)\"[^>]*>", r"\n![](\1)\n", s)
    s = re.sub(r"<sup>(.*?)</sup>", r"^\1", s)
    s = re.sub(r"<sub>(.*?)</sub>", r"_\1", s)
    s = re.sub(r"</?(strong|b)\b[^>]*>", "**", s)
    s = re.sub(r"</?(em|i)>", "*", s)
    s = re.sub(r"</?code>", "`", s)
    s = re.sub(r"<li[^>]*>\s*", "- ", s)
    s = re.sub(r"</li>|<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("\xa0", " ")
    s = re.sub(r"^[ \t]+- ", "- ", s, flags=re.M)
    s = re.sub(r"[ \t]+$", "", s, flags=re.M)
    s = re.sub(r"^(- [^\n]*)\n\n(?=- )", r"\1\n", s, flags=re.M)  # tight lists
    return re.sub(r"\n{3,}", "\n\n", s).strip() + "\n"


def signature(meta: dict) -> tuple[str, str]:
    """``(solver name, one-line signature)`` from LeetCode's metaData."""
    def ps(params: list) -> str:
        return ", ".join(f"{p['name']}: {p['type']}" for p in params)

    if "classname" in meta:
        ctor = ps((meta.get("constructor") or {}).get("params") or [])
        methods = ", ".join(m["name"] for m in meta.get("methods") or [])
        return meta["classname"], f"class {meta['classname']}({ctor}) · {methods}"
    ret = (meta.get("return") or {}).get("type", "?")
    return meta.get("name", ""), f"{meta.get('name')}({ps(meta.get('params') or [])}) -> {ret}"


def example_keys(examples: list[str]) -> set[str]:
    """Each example's argument values as an order-free key (bank cases are
    stored sorted by parameter name, so positional order is not recoverable)."""
    keys = set()
    for ex in examples:
        try:
            vals = [json.loads(line) for line in ex.split("\n") if line.strip()]
        except ValueError:
            continue
        keys.add(_canon(sorted(_canon(v) for v in vals)))
    return keys


def bank_example_keys(p: Problem) -> set[str]:
    keys = set()
    for inp in p.inputs:
        d = json.loads(inp)
        if isinstance(d, dict):
            keys.add(_canon(sorted(_canon(v) for v in d.values())))
    return keys


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def rank(bank: list[Problem], *, slug: str, title: str, fname: str,
         statement: str, examples: set[str]) -> list[dict]:
    n = len(bank) + 1

    want = _stemmed_tokens(slug, title)
    toks = {p.slug: _stemmed_tokens(p.slug, p.title) for p in bank}
    df: dict[str, int] = {}
    for ts in toks.values():
        for t in ts:
            df[t] = df.get(t, 0) + 1

    def idf(t: str) -> float:
        return math.log((n + 1) / (df.get(t, 0) + 1)) + 1.0

    want_weight = sum(idf(t) for t in want) or 1.0

    q_tf = statement_tokens(statement) if statement else {}
    bank_tf = {p.slug: statement_tokens(p.statement) for p in bank} if q_tf else {}
    sdf: dict[str, int] = {}
    for tf in bank_tf.values():
        for t in tf:
            sdf[t] = sdf.get(t, 0) + 1

    def weigh(tf: dict[str, int]) -> dict[str, float]:
        return {t: v * (math.log((n + 1) / (sdf.get(t, 0) + 1)) + 1.0)
                for t, v in tf.items()}

    q_w = weigh(q_tf)
    q_norm = math.sqrt(sum(x * x for x in q_w.values())) or 1.0

    out = []
    for p in bank:
        sig: dict[str, float] = {}
        if p.slug == slug:
            sig["slug"] = 1.0
        if title and norm_title(p.title) == norm_title(title):
            sig["title"] = 1.0
        name = sum(idf(t) for t in want & toks[p.slug]) / want_weight
        if name >= 0.3:
            sig["name"] = name
        if fname and fname not in GENERIC_FN_NAMES and p.fn_name == fname:
            sig["fname"] = 1.0
        if q_w:
            w = weigh(bank_tf[p.slug])
            dot = sum(v * w.get(t, 0.0) for t, v in q_w.items())
            norm = math.sqrt(sum(x * x for x in w.values())) or 1.0
            if dot / (q_norm * norm) >= 0.25:
                sig["stmt"] = dot / (q_norm * norm)
        hits = len(examples & bank_example_keys(p)) if examples else 0
        if hits:
            sig["example"] = float(hits)
        if not sig:
            continue
        score = (sig.get("slug", 0) + sig.get("title", 0) + sig.get("name", 0)
                 + sig.get("stmt", 0) + 0.5 * sig.get("fname", 0)
                 + 0.5 * min(hits, 2))
        out.append({"slug": p.slug, "root": p.root, "title": p.title,
                    "difficulty": p.difficulty, "score": score, "signals": sig})
    out.sort(key=lambda d: (-d["score"], d["slug"]))
    return out


def fmt_signals(sig: dict[str, float]) -> str:
    parts = []
    for k in ("slug", "title", "example", "fname", "name", "stmt"):
        if k not in sig:
            continue
        if k in ("name", "stmt"):
            parts.append(f"{k} {sig[k]:.2f}")
        elif k == "example":
            parts.append(f"example x{int(sig[k])}")
        else:
            parts.append(k)
    return " · ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("target", help="problem URL, LeetCode slug, or title")
    ap.add_argument("--title", help="the problem's title (for non-LeetCode URLs)")
    ap.add_argument("--statement", type=Path,
                    help="a file holding the statement (for the stmt signal)")
    ap.add_argument("--fn", default="", help="solver function or class name")
    ap.add_argument("--offline", action="store_true", help="don't fetch anything")
    ap.add_argument("--save", type=Path, metavar="DIR",
                    help="write everything fetched to DIR/<slug>.json")
    ap.add_argument("-n", "--limit", type=int, default=8, help="candidates shown")
    args = ap.parse_args()

    slug, lc_slug = parse_target(args.target)
    title = args.title or ""
    fname, statement, examples = args.fn, "", set()
    q = None
    if lc_slug and not args.offline:
        try:
            q = fetch_leetcode(lc_slug)
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            print(f"warning: LeetCode fetch failed ({e}); matching on the slug only",
                  file=sys.stderr)
        if q is None and not title:
            print(f"warning: LeetCode has no problem '{lc_slug}'", file=sys.stderr)

    record: dict = {"url": args.target, "slug": slug}
    if q:
        meta = json.loads(q.get("metaData") or "{}")
        fname = fname or signature(meta)[0]
        slug, title = q["titleSlug"], title or q["title"]
        statement = html_to_markdown(q["content"]) if q.get("content") else ""
        examples = example_keys(q.get("exampleTestcaseList") or [])
        raw_tags = [t["slug"] for t in q.get("topicTags") or []]
        snippet = next((c["code"] for c in q.get("codeSnippets") or []
                        if c["langSlug"] == "python3"), "")
        record.update({
            "id": int(q["questionFrontendId"]), "slug": slug, "title": q["title"],
            "difficulty": q["difficulty"].lower(), "paid": q["isPaidOnly"],
            "category": q.get("categoryTitle"), "tags_raw": raw_tags,
            "tags_canonical": normalize_tags(raw_tags), "meta": meta,
            "python_snippet": snippet,
            "examples": q.get("exampleTestcaseList") or [],
            "statement_source": q["source"], "statement_html": q.get("content"),
            "statement_md": statement or None,
            "images": re.findall(r"<img[^>]*?src=\"([^\"]+)\"", q.get("content") or ""),
        })
        print(f"LeetCode {record['id']} · {q['title']} · {record['difficulty']}"
              f" · {'premium' if q['isPaidOnly'] else 'free'} · {q.get('categoryTitle')}")
        print(f"  tags      {', '.join(raw_tags) or '-'}")
        print(f"  canonical {', '.join(record['tags_canonical']) or '-'}")
        print(f"  solver    {signature(meta)[1]}")
        src = {"leetcode": "LeetCode", "doocs": "doocs/leetcode mirror"}
        print(f"  statement {src.get(q['source'] or '', 'UNAVAILABLE - find it elsewhere')}"
              f" · {len(examples)} example(s) · {len(record['images'])} figure(s)")
        if q.get("categoryTitle") not in (None, "Algorithms"):
            print(f"  WARNING   {q['categoryTitle']} problem: the harness only judges "
                  "Python functions/classes")
    if args.statement:
        statement = args.statement.read_text()
    if not slug and not title:
        print("error: nothing to look up", file=sys.stderr)
        return 2
    title = title or slug.replace("-", " ")

    if args.save:
        args.save.mkdir(parents=True, exist_ok=True)
        out = args.save / f"{slug}.json"
        out.write_text(json.dumps(record, indent=2) + "\n")
        print(f"  saved     {out}")

    bank = load_bank(list(settings.content_dirs))
    hits = rank(bank, slug=slug, title=title, fname=fname, statement=statement,
                examples=examples)
    roots = ", ".join(sorted({p.root for p in bank}))
    print(f"\nBank: {len(bank)} problems ({roots})")

    # The slug match first: when the bank already holds a twin under another
    # slug, the one named after the URL is the answer.
    exact = sorted((h for h in hits if {"slug", "title"} & h["signals"].keys()),
                   key=lambda h: "slug" not in h["signals"])
    likely = [h for h in hits if h["signals"].get("example", 0) >= 2
              or ("example" in h["signals"] and "fname" in h["signals"])]
    if exact:
        h = exact[0]
        print(f"VERDICT: IN BANK — {h['slug']} ({h['root']}) \"{h['title']}\" "
              f"[{h['difficulty']}] · matched on {fmt_signals(h['signals'])}")
        for twin in exact[1:]:
            print(f"         also {twin['slug']} ({twin['root']}) · matched on "
                  f"{fmt_signals(twin['signals'])}")
        code = 0
    elif likely:
        h = likely[0]
        print(f"VERDICT: LIKELY IN BANK — {h['slug']} ({h['root']}) \"{h['title']}\" "
              "grades the same example input(s); read it to confirm")
        code = 3
    else:
        print("VERDICT: NOT FOUND — no slug, title or example match"
              + ("; read the candidates below before adding" if hits else ""))
        code = 1

    if hits:
        shown = hits[:args.limit]
        w = max(len(h["slug"]) for h in shown)
        print(f"\n{'score':>5}  {'slug':{w}}  {'root':17}  signals")
        for h in shown:
            print(f"{h['score']:5.2f}  {h['slug']:{w}}  {h['root']:17}  "
                  f"{fmt_signals(h['signals'])}")
    return code


if __name__ == "__main__":
    sys.exit(main())
