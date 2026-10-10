"""The optional-extension seam: what it does, and what it must not do.

The contract worth pinning is the *absence* case. An extension folder can be
deleted (or never cloned), and when it is, lootcode has to be exactly what it
was: no nav item, no routes, no identity roots, no error at startup. The last
test here proves that by starting the real app with the import of the
extension package blocked.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from app import extensions
from app.extensions import ExtensionInfo, NavItem, Registry, load_extensions
from app.main import _wants_identity


@pytest.fixture
def registry():
    return Registry()


def test_a_missing_extension_is_skipped_silently(registry):
    loaded = load_extensions(object(), names=("definitely_not_installed",),
                             registry=registry)
    assert loaded == []
    assert registry.nav == []
    assert registry.identity_roots == ()


def test_an_extension_that_fails_to_import_its_own_dependency_is_loud(
        registry, monkeypatch):
    """A *broken* extension must not look like an absent one."""
    def explode(name):
        raise ModuleNotFoundError("No module named 'requests'", name="requests")

    monkeypatch.setattr(extensions.importlib, "import_module", explode)
    with pytest.raises(ModuleNotFoundError):
        load_extensions(object(), names=("pretend",), registry=registry)


def test_an_extension_must_offer_register(registry, monkeypatch):
    monkeypatch.setattr(extensions.importlib, "import_module",
                        lambda name: object())
    with pytest.raises(RuntimeError, match="register"):
        load_extensions(object(), names=("pretend",), registry=registry)


def test_register_must_return_an_extension_info(registry, monkeypatch):
    class Module:
        @staticmethod
        def register(app):
            return {"name": "pretend"}

    monkeypatch.setattr(extensions.importlib, "import_module", lambda name: Module)
    with pytest.raises(RuntimeError, match="ExtensionInfo"):
        load_extensions(object(), names=("pretend",), registry=registry)


def test_what_an_extension_registers_reaches_the_registry(registry, monkeypatch):
    info = ExtensionInfo(name="pretend",
                         nav=(NavItem(label="Pretend", href="/pretend"),),
                         identity_roots=("/pretend",))

    class Module:
        @staticmethod
        def register(app):
            return info

    monkeypatch.setattr(extensions.importlib, "import_module", lambda name: Module)
    load_extensions(object(), names=("pretend",), registry=registry)
    assert registry.names == ["pretend"]
    assert registry.nav[0].href == "/pretend"
    assert registry.identity_roots == ("/pretend",)


def test_identity_is_granted_to_registered_roots_and_nothing_near_them(monkeypatch):
    monkeypatch.setattr(extensions.REGISTRY, "loaded",
                        [ExtensionInfo(name="pretend", identity_roots=("/pretend",))])
    assert _wants_identity("/pretend")
    assert _wants_identity("/pretend/thing")
    assert not _wants_identity("/pretend.php"), "a prefix test would match this"
    assert not _wants_identity("/pretending")


def test_the_header_renders_registered_links(client, monkeypatch):
    monkeypatch.setattr(
        extensions.REGISTRY, "loaded",
        [ExtensionInfo(name="pretend",
                       nav=(NavItem(label="Pretend", href="/pretend",
                                    title="a pretend feature"),))])
    body = client.get("/").text
    assert '<a href="/pretend" title="a pretend feature">Pretend</a>' in body


# --- the one that matters -------------------------------------------------

_ABSENT_EXTENSION = '''
import sys, importlib.abc, tempfile, os

BLOCKED = {name!r}

class Blocker(importlib.abc.MetaPathFinder):
    """Make the extension package look like it was never cloned."""
    def find_spec(self, fullname, path=None, target=None):
        if fullname == BLOCKED or fullname.startswith(BLOCKED + "."):
            raise ModuleNotFoundError("No module named " + repr(fullname),
                                      name=fullname)
        return None

sys.meta_path.insert(0, Blocker())
os.environ["LOOTCODE_DB"] = os.path.join(tempfile.mkdtemp(), "absent.db")

from fastapi.testclient import TestClient          # noqa: E402
from app.db import init_db                         # noqa: E402
from app.extensions import REGISTRY                # noqa: E402
from app.main import app                           # noqa: E402

init_db()   # the lifespan is not run here; the identity middleware needs users

assert REGISTRY.names == [], REGISTRY.names
assert REGISTRY.nav == []

client = TestClient(app)
home = client.get("/")
assert home.status_code == 200, home.status_code
assert "/" + BLOCKED not in home.text, "the nav still links to the extension"
for path in ("/" + BLOCKED, "/" + BLOCKED + "/anything",
             "/api/" + BLOCKED + "/anything"):
    assert client.get(path).status_code == 404, path
print("ok")
'''


@pytest.mark.slow
@pytest.mark.parametrize("name", sorted(extensions.OPTIONAL_EXTENSIONS))
def test_the_app_is_unchanged_when_an_extension_is_absent(name, tmp_path):
    """Start the real app with the extension unimportable: it must not notice."""
    script = tmp_path / "absent.py"
    script.write_text(textwrap.dedent(_ABSENT_EXTENSION).format(name=name),
                      encoding="utf-8")
    repo_root = Path(__file__).resolve().parent.parent
    # The script lives in a temp dir, so sys.path[0] is not the repo: point
    # PYTHONPATH at it rather than relying on the working directory.
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True,
        cwd=str(repo_root), env={**os.environ, "PYTHONPATH": str(repo_root)})
    assert result.returncode == 0, result.stdout + result.stderr
