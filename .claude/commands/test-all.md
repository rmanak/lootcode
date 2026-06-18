---
description: Run the pytest suite and summarize failures
allowed-tools: Bash(.venv/bin/python -m pytest:*), Bash(python -m pytest:*)
---

Run the test suite with `.venv/bin/python -m pytest -q` (fall back to
`python -m pytest -q` if there's no venv).

Summarize results compactly. For each failure give the test name, the cause, and
the smallest fix. Pay special attention to `tests/test_executor.py` — those
guard the sandbox. Do not change any code unless I explicitly ask.
