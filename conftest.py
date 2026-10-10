"""Repo-root pytest bootstrap.

Two jobs, both about *optional extensions* (see app/extensions.py), and both
written so they are no-ops when no extension is installed:

1. **Collect the extension's own tests.** ``testpaths`` in pyproject.toml is
   ``tests``, deliberately, so a bare ``pytest`` does not wander into
   ``scripts/``. An extension keeps its tests inside its own folder, which that
   setting would then never see.

2. **Redirect the extension's database.** Core's suite redirects
   ``LOOTCODE_DB`` in tests/conftest.py for exactly this reason; an extension
   with its own database file needs the same protection, and the redirect has
   to happen before anything imports it. The names are known here — in the test
   harness — rather than in the application.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_TMP = Path(tempfile.mkdtemp(prefix="lootcode-ext-tests-"))

# Core's suite redirects LOOTCODE_DB in tests/conftest.py, but that file is only
# loaded when `tests/` is being collected: running an extension's suite on its
# own (`pytest icf/tests`) started the app against the developer's live
# database, and every request that mints a guest wrote a row into it. The
# redirect therefore also happens here, at the root, where it covers every
# invocation. tests/conftest.py overwrites this with its own temp path and
# still asserts the result is not the real file.
os.environ["LOOTCODE_DB"] = str(_TMP / "lootcode-test.db")

#: Extension name -> (env var for its database, the test database file).
_EXTENSION_DATABASES = {"icf": ("ICF_DB", _TMP / "icf-test.db")}

for name, (env_var, path) in _EXTENSION_DATABASES.items():
    if (ROOT / name).is_dir():
        os.environ[env_var] = str(path)


def _extension_test_dirs() -> list[Path]:
    return [d for name in _EXTENSION_DATABASES
            if (d := ROOT / name / "tests").is_dir()]


def pytest_configure(config) -> None:
    for tests_dir in _extension_test_dirs():
        already = any(
            tests_dir == Path(arg).resolve() or tests_dir in Path(arg).resolve().parents
            for arg in config.args)
        if not already:
            config.args.append(str(tests_dir))


def pytest_unconfigure(config) -> None:
    shutil.rmtree(_TMP, ignore_errors=True)
