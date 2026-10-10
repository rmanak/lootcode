"""Industry Coding Framework — an optional lootcode extension.

Four-level, time-capped assessments in the CodeSignal "industry coding" shape:
the solver implements one class from a template, each level adds requirements
while the earlier levels must keep passing, and every level is gated behind its
own unit tests.

**Delete this folder and lootcode is exactly what it was.** Core discovers the
package by name at startup (``app/extensions.py``); if the import fails because
the folder is gone, nothing is mounted, the nav link is not rendered, and the
routes below do not exist. Nothing in ``app/`` imports anything from here — the
arrow points one way, the same way ``authoring/`` points at ``app/``.

What lives where:

===========================  ==================================================
``config.py``                settings (its own env vars, its own defaults)
``content.py``               load + validate problems from ``icf/problems/``
``db.py`` / ``models.py``    its **own** SQLite file — never lootcode.db
``store.py``                 attempt lifecycle: clock, unlocking, runs, drafts
``runner.py``                grade a submission through core's sandbox
``sandbox/``                 what runs *inside* the sandbox (stdlib only)
``views.py``                 JSON shaping, and the hidden-test redaction rule
``routers/``                 pages (``/icf``) and API (``/api/icf``)
``problems/``                the problem definitions themselves
``scripts/verify_icf.py``    the gate: every canonical passes every level
===========================  ==================================================
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi.staticfiles import StaticFiles
from jinja2 import ChoiceLoader, FileSystemLoader

from app.extensions import ExtensionInfo, NavItem

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"

#: Mounted under /icf, so these can never be problem slugs (enforced by
#: content.RESERVED_SLUGS).
STATIC_MOUNT = "/icf/static"


def _static_url(path: str) -> str:
    """``icf_static('icf.css')`` with an mtime cache-buster, mirroring core's
    ``static()`` helper so an edited stylesheet is never served from cache."""
    try:
        version = int(os.path.getmtime(STATIC_DIR / path))
    except OSError:
        return f"{STATIC_MOUNT}/{path}"
    return f"{STATIC_MOUNT}/{path}?v={version}"


def register(app) -> ExtensionInfo:
    """Mount the feature onto a running lootcode app. Called by core's loader."""
    from app.templating import templates

    from .routers import api, pages

    # Our templates extend core's base.html, so they join the *same* Jinja
    # environment rather than getting one of their own (which could not see
    # base.html, `static()` or the markdown filter). Ours is appended, so a
    # name clash resolves to core's file.
    env = templates.env
    ours = FileSystemLoader(str(TEMPLATES_DIR))
    env.loader = ChoiceLoader([env.loader, ours]) if env.loader else ours
    env.globals.setdefault("icf_static", _static_url)

    # Mounted before the routes so /icf/static never looks like /icf/{slug}.
    app.mount(STATIC_MOUNT, StaticFiles(directory=str(STATIC_DIR)),
              name="icf-static")
    app.include_router(pages.router)
    app.include_router(api.router)

    return ExtensionInfo(
        name="icf",
        nav=(NavItem(label="🏭 Industry", href="/icf",
                     title="Industry Coding Framework — timed, 4-level "
                           "assessments"),),
        # /icf pages extend base.html, which reads request.state.is_account.
        # (/api/icf is already covered by core's "/api" root.)
        identity_roots=("/icf",),
    )
