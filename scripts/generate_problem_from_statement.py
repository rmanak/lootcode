#!/usr/bin/env python3
"""Generate a lootcode problem from a fixed problem statement, via an LLM endpoint.

This is the **command-line driver** for the "Mode A — fill-in" generation flow
(see ``docs/problem-generation.md``): you already have the problem *statement*, and
the model produces everything else needed to make it runnable and auto-gradable —
the function/class contract, a starter stub, a canonical reference solution, hints,
and a test suite. The model never rewrites the statement it was handed.

Pieces it ties together:
  * ``app/llm/problem_prompt.txt``  — the prompt template (self-contained; the
    statement is injected in place of the ``{{PROBLEM_STATEMENT}}`` token).
  * this script                     — injects the statement, calls an
    OpenAI-compatible endpoint asking for **schema-constrained JSON**, then (by
    default) verifies the result and retries once on failure before emitting it.
  * ``scripts/test_llm_output.py``  — STATIC schema/semantic validation.
  * ``scripts/verify_json.py``      — BEHAVIORAL check: actually runs the
    ``canonical_solution`` against the tests in the sandbox.

Verify-and-retry (``--verify`` / ``--no-verify``, on by default)
----------------------------------------------------------------
After each completion the object is checked by :func:`verify_output` — static
(schema + semantics) *and* behavioral (the canonical must produce every test's
declared ``expected`` when run). If it fails, the model is re-prompted with the
concrete errors and asked to redo it, up to ``--max-retries`` times (default 1);
if it still fails the object is written/emitted anyway (for inspection) but the
run is reported as failed (non-zero exit / counted as a batch failure). This is
what catches a *buggy canonical* or *wrong expected value* that static validation
alone (which never runs the code) lets through.

Auto kind is resolved first by a cheap no-thinking :func:`classify_kind` call, so
each request carries a single tight per-kind schema (see ``problem_schema``).

The request is sent with an OpenAI-style ``response_format`` JSON schema
(``PROBLEM_SCHEMA`` below). Against a llama.cpp ``llama-server`` this triggers
constrained decoding, so the reply is *guaranteed* to be schema-valid JSON; against
other OpenAI-compatible endpoints it is a strong steer, and we degrade to laxer
response formats if a bare endpoint rejects the schema.

``PROBLEM_SCHEMA`` is kept consistent with the data model on purpose: it mirrors the
contract enforced by ``scripts/test_llm_output.py`` (``ProblemOutput``) and, through
it, ``specs/problem-schema.md``. If that contract changes (a new field, a new
``compare`` mode, a new problem ``kind``), update all three together.

Usage
-----
    # local llama-server (default endpoint), statement in a text file:
    python scripts/generate_problem_from_statement.py statement.txt -o problem.json

    # folder mode: for each <dir>/<slug>/problem.md, write the generated object to
    # <dir>/<slug>/generated_full_problem.json (resumable; skips existing outputs).
    # <dir> is any staging folder of <slug>/ subdirs — the name is arbitrary:
    python scripts/generate_problem_from_statement.py path/to/staging/

    # ...same, but keep 3 LLM requests in flight (match a server's --parallel):
    python scripts/generate_problem_from_statement.py path/to/staging/ -j 3

    # skip verification (emit the first completion unchecked, fastest):
    python scripts/generate_problem_from_statement.py statement.txt --no-verify

    # a hosted OpenAI-compatible endpoint:
    OPENAI_API_KEY=sk-... python scripts/generate_problem_from_statement.py \
        statement.txt --base-url https://api.openai.com/v1 --model gpt-4o

Endpoint defaults come from the same environment variables the app uses
(``LLM_HELP_URL`` / ``LLM_HELP_MODEL`` / ``LLM_HELP_API_KEY``), so a shell already
configured for lootcode's AI features works with no extra flags.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Repo root on sys.path so `app` resolves when this is run from anywhere.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# The generation itself lives in the runtime package: the admin "Generate with
# AI" page runs this exact code, so the two front ends cannot drift.
from app.llm.fill_in import (  # noqa: E402
    GENERATED_FILENAME,
    STATEMENT_FILENAME,
    generate,
    warn_if_tags_drifted,
)


def _process_one(d: Path, prefix: str, *, gen_kwargs: dict, overwrite: bool) -> str:
    """Generate + write the object for a single ``<slug>/`` folder.

    Returns ``"ok"``, ``"fail"``, or ``"skip"``. All progress/diagnostics are
    buffered and emitted to stderr in ONE write so lines from concurrent workers
    don't interleave. Resumability lives here: an existing output is skipped unless
    ``overwrite``, so re-running the batch only fills in the gaps.
    """
    slug = d.name
    out_path = d / GENERATED_FILENAME
    if out_path.exists() and not overwrite:
        sys.stderr.write(f"SKIP {prefix} {slug}: {GENERATED_FILENAME} exists "
                         "(use --overwrite to regenerate)\n")
        return "skip"
    statement = (d / STATEMENT_FILENAME).read_text(encoding="utf-8").strip()
    if not statement:
        sys.stderr.write(f"FAIL {prefix} {slug}: {STATEMENT_FILENAME} is empty\n")
        return "fail"
    sys.stderr.write(f"---> {prefix} {slug}: generating...\n")
    try:
        res = generate(statement, **gen_kwargs)
    except (Exception, SystemExit) as e:  # noqa: BLE001 - isolate per-slug failures
        sys.stderr.write(f"FAIL {prefix} {slug}: generation error: {e}\n")
        return "fail"
    # Keep the object on disk either way, so a failed one can be inspected/fixed.
    out_path.write_text(json.dumps(res.data, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    if res.verified:
        sys.stderr.write(f"OK   {prefix} {slug}: wrote {out_path}\n")
        return "ok"
    lines = [f"     ERROR: {err}\n" for err in res.errors]
    sys.stderr.write(
        f"FAIL {prefix} {slug}: verification failed after {res.attempts} attempt(s) "
        f"(kept at {out_path} for inspection).\n" + "".join(lines))
    return "fail"


def _run_batch(root: Path, *, gen_kwargs: dict, overwrite: bool, jobs: int = 1) -> int:
    """Folder mode: generate a full problem for every ``<root>/<slug>/problem.md``.

    Each subdirectory of *root* that holds a ``problem.md`` is treated as one
    problem: the statement is read, the model fills in the rest (verifying + retrying
    per ``gen_kwargs``), and the object is written to
    ``<root>/<slug>/generated_full_problem.json``. One slug failing (generation
    error, empty statement, failed verification) never aborts the batch — the run is
    resumable, so an existing output is skipped unless ``--overwrite``, and a failed
    object is still written to disk for inspection. Returns 0 iff nothing failed.

    With ``jobs > 1`` the slugs are dispatched across a thread pool so that many LLM
    requests are in flight at once (the work is I/O-bound on the endpoint) — point it
    at a server started with matching ``--parallel``. Each worker builds its own
    client, and resumability is unchanged: skip-existing is decided per slug, so a
    parallel re-run still only fills the gaps.
    """
    slug_dirs = sorted(
        d for d in root.iterdir()
        if d.is_dir() and (d / STATEMENT_FILENAME).is_file())
    if not slug_dirs:
        sys.stderr.write(
            f"ERROR: no <slug>/{STATEMENT_FILENAME} found under {root}\n")
        return 2

    total = len(slug_dirs)
    jobs = max(1, min(jobs, total))
    counts = {"ok": 0, "fail": 0, "skip": 0}

    if jobs == 1:
        for i, d in enumerate(slug_dirs, 1):
            status = _process_one(d, f"[{i}/{total}]", gen_kwargs=gen_kwargs,
                                  overwrite=overwrite)
            counts[status] += 1
    else:
        from concurrent.futures import ThreadPoolExecutor, as_completed  # noqa: PLC0415
        sys.stderr.write(f"Running {total} problem(s) with {jobs} parallel worker(s).\n")
        done = 0
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            futures = {
                pool.submit(_process_one, d, "", gen_kwargs=gen_kwargs,
                            overwrite=overwrite): d
                for d in slug_dirs
            }
            for fut in as_completed(futures):
                done += 1
                try:
                    status = fut.result()
                except Exception as e:  # noqa: BLE001 - defensive: worker should not raise
                    sys.stderr.write(
                        f"FAIL [{done}/{total}] {futures[fut].name}: worker error: {e}\n")
                    status = "fail"
                counts[status] += 1

    sys.stderr.write(
        f"\nBatch done ({total} problem folder(s)): "
        f"{counts['ok']} ok, {counts['fail']} failed, {counts['skip']} skipped.\n")
    return 0 if counts["fail"] == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a lootcode problem (contract + solution + tests + "
                    "hints) from a problem-statement file, via an OpenAI-compatible "
                    "LLM endpoint with schema-constrained JSON output.")
    parser.add_argument("input", metavar="PATH",
                        help="Either a single text/Markdown file with the problem "
                             f"statement, OR a folder — in folder mode, each "
                             f"<PATH>/<slug>/{STATEMENT_FILENAME} is generated and "
                             f"written to <PATH>/<slug>/{GENERATED_FILENAME}.")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="Single-file mode only: write the JSON here "
                             "(default: stdout). Ignored in folder mode.")
    parser.add_argument("--overwrite", action="store_true",
                        help=f"Folder mode only: regenerate even if a "
                             f"{GENERATED_FILENAME} already exists (default: skip it, "
                             "so a batch is resumable).")
    parser.add_argument("-j", "--jobs", type=int, default=1, metavar="N",
                        help="Folder mode only: number of slugs to generate in "
                             "parallel (default: 1). Each worker opens its own "
                             "connection, so match N to the endpoint's capacity "
                             "(e.g. llama-server --parallel N). Resumability is "
                             "unchanged — already-generated outputs are still "
                             "skipped.")
    parser.add_argument("--kind", choices=("auto", "function", "class"), default="auto",
                        help="Pin the problem kind (default: auto — the model "
                             "decides). Use 'class' for a folder of design problems: "
                             "it hard-requires class_name/class_methods and constrains "
                             "each test to {operations,args} -> output list, closing "
                             "the ways a design problem comes back malformed.")
    parser.add_argument("--base-url",
                        default=os.environ.get("LLM_HELP_URL",
                                               os.environ.get("OPENAI_BASE_URL",
                                                              "http://localhost:8080")),
                        help="OpenAI-compatible base URL (default: $LLM_HELP_URL or "
                             "http://localhost:8080). '/v1' is appended if missing.")
    parser.add_argument("--model",
                        default=os.environ.get("LLM_HELP_MODEL",
                                               os.environ.get("OPENAI_MODEL", "qwen36")),
                        help="Model id (default: $LLM_HELP_MODEL or 'qwen36').")
    parser.add_argument("--api-key",
                        default=os.environ.get("LLM_HELP_API_KEY",
                                               os.environ.get("OPENAI_API_KEY",
                                                              "sk-no-key-required")),
                        help="API key (default: $LLM_HELP_API_KEY / $OPENAI_API_KEY; "
                             "a placeholder is fine for a local server).")
    parser.add_argument("--temperature", type=float, default=None,
                        help="Sampling temperature. Omitted unless set, so the "
                             "server's own default governs sampling.")
    parser.add_argument("--max-tokens", type=int, default=16000,
                        help="Max completion tokens (default: 16000).")
    parser.add_argument("--reasoning", choices=("off", "on", "keep"), default="keep",
                        help="Model 'thinking' knob for llama.cpp/Qwen: keep (default) "
                             "omits the param so the server decides (and works with "
                             "stock OpenAI endpoints), off disables thinking for "
                             "cleaner JSON, on enables it.")
    parser.add_argument("--verify", action=argparse.BooleanOptionalAction, default=True,
                        help="Verify each result and retry once on failure (default: "
                             "on). Verification is STATIC (schema/semantic via "
                             "test_llm_output.py) AND BEHAVIORAL (runs the "
                             "canonical_solution against the tests in the sandbox); on "
                             "failure the model is re-prompted with the errors. "
                             "Use --no-verify to just emit the first completion.")
    parser.add_argument("--max-retries", type=int, default=1,
                        help="How many times to re-prompt the model after a failed "
                             "verification before skipping (default: 1). Ignored with "
                             "--no-verify.")
    parser.add_argument("--strict", action="store_true",
                        help="Treat validation warnings as failures too.")
    parser.add_argument("--no-validate", action="store_true",
                        help=argparse.SUPPRESS)  # deprecated alias for --no-verify
    args = parser.parse_args(argv)
    # Back-compat: the old --no-validate flag disables the whole verify pipeline.
    verify = args.verify and not args.no_validate

    path = Path(args.input)
    if not path.exists():
        sys.stderr.write(f"ERROR: input path not found: {path}\n")
        return 2

    warn_if_tags_drifted()

    gen_kwargs = {"base_url": args.base_url, "model": args.model, "api_key": args.api_key,
                      "temperature": args.temperature, "max_tokens": args.max_tokens,
                      "reasoning": args.reasoning, "kind": args.kind, "verify": verify,
                      "max_retries": args.max_retries, "strict": args.strict}

    # Folder mode: PATH is a directory of <slug>/problem.md problem folders.
    if path.is_dir():
        if args.output:
            sys.stderr.write(
                "ERROR: -o/--output does not apply in folder mode; each problem is "
                f"written to <slug>/{GENERATED_FILENAME}.\n")
            return 2
        if args.jobs < 1:
            sys.stderr.write("ERROR: -j/--jobs must be >= 1\n")
            return 2
        return _run_batch(path, gen_kwargs=gen_kwargs, overwrite=args.overwrite,
                          jobs=args.jobs)

    # Single-file mode.
    statement = path.read_text(encoding="utf-8").strip()
    if not statement:
        sys.stderr.write(f"ERROR: statement file is empty: {path}\n")
        return 2

    res = generate(statement, **gen_kwargs)

    rendered = json.dumps(res.data, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        sys.stderr.write(f"Wrote {args.output}\n")
    else:
        print(rendered)

    if not verify:
        return 0
    if res.verified:
        sys.stderr.write(
            f"OK: generated problem verified (schema + canonical passes all tests"
            f"{'' if res.attempts == 1 else f'; took {res.attempts} attempt(s)'}).\n")
        return 0
    for err in res.errors:
        sys.stderr.write(f"ERROR: {err}\n")
    sys.stderr.write(
        f"INVALID: verification failed after {res.attempts} attempt(s) "
        f"({len(res.errors)} error(s)).\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
