#!/usr/bin/env python3
"""CLI for the structural problem validator.

    python scripts/test_llm_output.py generated_llm_output.json [--strict]

The checks themselves live in ``app/problem_spec.py``. They used to live here,
and ``app/problem_validation.py`` reached them by inserting ``scripts/`` onto
``sys.path`` at import time — on the request path — so the runtime depended on
the tooling directory. The arrow now points the other way.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.problem_spec import (  # noqa: E402
    ProblemOutput,
    Report,
    load_json_object,
    semantic_checks,
    validate,
)

__all__ = ["ProblemOutput", "Report", "load_json_object", "semantic_checks", "validate"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate LLM-generated problem JSON for lootcode "
                    "(see app/llm/problem_prompt.txt).",
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file containing the LLM's structured output.",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat warnings as errors (exit non-zero if any warning).",
    )
    args = parser.parse_args(argv)

    path = Path(args.json_file)
    data = load_json_object(path)          # exits 2 on unreadable/non-object JSON
    rep = validate(data, strict=args.strict)

    # ---- print the report ----
    for w in rep.warnings:
        print(f"WARN:  {w}")
    for e in rep.errors:
        print(f"ERROR: {e}")

    if rep.ok(strict=args.strict):
        suffix = "" if not rep.warnings else f" ({len(rep.warnings)} warning(s))"
        print(f"OK: {path} is a valid problem-generation output{suffix}.")
        return 0

    print(
        f"INVALID: {path} has {len(rep.errors)} error(s) and "
        f"{len(rep.warnings)} warning(s)."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
