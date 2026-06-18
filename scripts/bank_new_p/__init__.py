"""Batch-authored problems imported from `new_p.txt` (LeetCode URL dump).

Each `batch_NNN.py` module does `from scripts.build_bank import add, COMPARE, ...`
and registers ~20 problems by calling `add(...)` at import time, appending to the
shared `PROBLEMS` list in `scripts.build_bank`. Importing this package (done from
`build_bank.py`'s `__main__`, after that module is fully defined, so there is no
circular import) pulls in every batch in sorted order.

The set of slugs defined across these batch files is the durable record of what has
already been imported; `_worklist.py` uses it to compute the next undone chunk.
"""
import importlib
from pathlib import Path

_pkg_dir = Path(__file__).resolve().parent
for _name in sorted(p.stem for p in _pkg_dir.glob("batch_*.py")):
    importlib.import_module(f"{__name__}.{_name}")
