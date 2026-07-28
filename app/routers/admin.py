"""The `/admin` surface, assembled from its two halves.

This module was 800 lines doing four jobs at once. It is now just the mount
point, so `main.py` and every existing `/admin/...` URL are unchanged:

- `admin_problems.py` — list, edit, verify, create. The CRUD, and the one
  validated save path every write goes through.
- `admin_generate.py`  — the AI flow (idea → statement → draft → review), which
  touches almost nothing in the CRUD half and ends by handing the owner back to
  it at `POST /admin/new`.
- `admin_forms.py`     — the marshalling both halves share.

No real auth (this is a home/LAN instance) — see `docs/security.md` for the
trust boundary. If you expose lootcode beyond a trusted network, put this
router behind authentication.
"""
from __future__ import annotations

from fastapi import APIRouter

from . import admin_generate, admin_problems

PREFIX = "/admin"

router = APIRouter()

# Generation first: its paths are all under /admin/generate and none of them can
# be shadowed by the CRUD routes, but keeping the more specific mount first means
# that stays true if either side grows a wildcard.
#
# The prefix is applied here rather than on the sub-routers so it is written
# once, and because FastAPI refuses to include a router whose prefix *and* route
# path are both empty — which the dashboard's `@router.get("")` would be.
router.include_router(admin_generate.router, prefix=PREFIX)
router.include_router(admin_problems.router, prefix=PREFIX)
