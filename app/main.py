"""FastAPI application: server-rendered UI + JSON run API.

Run locally:   uvicorn app.main:app --reload
Or:            python -m app.main      (honours HOST/PORT from .env)
"""
from __future__ import annotations

import ipaddress
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from starlette.concurrency import run_in_threadpool

from .config import settings
from .db import SessionLocal, init_db
from .logging_config import configure_logging, get_logger
from .models import Problem, User
from .routers import admin, pages, submissions
from .store import seed_collections, seed_from_content

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    # Before anything else: an unauthenticated app must not come up on the
    # network by accident, however it was launched.
    check_bind_is_intentional(effective_bind_host())
    log.info("starting %s (db=%s)", settings.APP_NAME, settings.DB_PATH)
    init_db()
    with SessionLocal() as db:
        if not db.scalar(select(func.count()).select_from(Problem)):
            log.info("empty database — seeding from %s",
                     ", ".join(str(p) for p in settings.content_dirs))
            seed_from_content(db)
        # Curated lists are cheap to rebuild and idempotent, so (re)seed them on
        # every startup — a manifest edit takes effect on restart without a full
        # problem re-seed. Unknown slugs are logged, not fatal (see store).
        seed_collections(db)

    # Probe the optional "Get More Help with AI" endpoint once. The problem page
    # enables the button only when this succeeds; any failure just leaves it off.
    # It can be re-probed later without a restart via POST /api/llm/refresh (the
    # "re-check" buttons on the admin and problem pages).
    try:
        from .llm.help_generator import refresh_availability

        refresh_availability()
    except Exception:  # noqa: BLE001 - never let an optional probe block startup
        settings.llm_help_available = False
    log.info("AI help endpoint %s",
             "available" if settings.llm_help_available else "unavailable")
    yield
    log.info("shutting down")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")


# Paths that get an identity. Everything else — the JSON API called by a script,
# a bot probing /wp-login.php, a 404 — is served without minting a `User` row.
# Before this, every request without a valid cookie created a guest, forever:
# the users table grew one row per crawler hit and per 404, each one a write on
# the request path.
_IDENTITY_ROOTS = ("/problems", "/api", "/admin", "/me", "/account",
                   "/login", "/logout", "/random")
_IDENTITY_EXACT = frozenset({"/"})


def _wants_identity(path: str) -> bool:
    # Segment-wise, not `startswith`: a bare prefix test also matches
    # "/admin.php" and "/api-docs.bak", which is exactly the scanner traffic
    # this is here to stop minting rows for.
    return path in _IDENTITY_EXACT or any(
        path == root or path.startswith(root + "/") for root in _IDENTITY_ROOTS)


def _load_or_create_user(uid: str | None) -> tuple[dict, bool]:
    """Resolve the cookie to a user, minting a guest if there isn't one.

    Synchronous on purpose, and called through a threadpool: this is blocking
    SQLite I/O, and it used to run directly on the event loop on *every* request
    — the one real blocking-async violation in the app, and the reason the SSE
    streams stalled while another request was writing.
    """
    with SessionLocal() as db:
        user = db.get(User, uid) if uid else None
        is_new = user is None
        if user is None:
            user = User(name="guest")
            db.add(user)
            db.commit()
            db.refresh(user)
        return {
            "user_id": user.id,
            "user_name": user.name,
            # V2: templates show login vs account state from these (see base.html).
            "is_account": user.is_account,
            "username": user.username,
        }, is_new


@app.middleware("http")
async def attach_user(request: Request, call_next):
    """Give every visitor a cookie-based identity (no passwords).

    Only for paths that actually render or act for a person — see
    ``_wants_identity``. Static assets, the favicon and unmatched paths go
    straight through.
    """
    if not _wants_identity(request.url.path):
        return await call_next(request)

    state, is_new = await run_in_threadpool(
        _load_or_create_user, request.cookies.get("lc_uid"))
    for key, value in state.items():
        setattr(request.state, key, value)

    response = await call_next(request)
    if is_new:
        response.set_cookie("lc_uid", state["user_id"], max_age=63_072_000,
                            httponly=True, samesite="lax")
    return response


app.include_router(pages.router)
app.include_router(submissions.router)
app.include_router(admin.router)


def effective_bind_host() -> str:
    """Best-effort guess at the host this process will actually listen on.

    ``python -m app.main`` reads ``settings.HOST``, but the documented way to run
    lootcode is ``uvicorn app.main:app``, where the bind comes from uvicorn's own
    ``--host`` flag or its ``UVICORN_HOST`` envvar and the app never sees it. The
    lifespan runs inside that process, so the command line is right there.
    """
    env_host = os.environ.get("UVICORN_HOST", "").strip()
    if env_host:
        return env_host
    argv = sys.argv[1:]
    for i, arg in enumerate(argv):
        if arg == "--host" and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith("--host="):
            return arg.split("=", 1)[1]
    return settings.HOST


def _is_loopback(host: str) -> bool:
    """Whether binding to ``host`` keeps the app off the network."""
    if host in ("localhost", ""):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        # A hostname we can't classify. Treat it as exposed: the whole point of
        # this check is to fail closed.
        return False


def check_bind_is_intentional(host: str) -> None:
    """Refuse to start on a non-loopback bind unless the operator opted in.

    lootcode has **no authentication**: ``/admin/*`` can rewrite the problem
    bank, ``POST /admin/verify`` executes arbitrary submitted Python, and the
    default subprocess sandbox does not block network access. The security
    boundary is the network, and the owner's decision is that this is the right
    trade for a single-user LAN instance (see docs/security.md).

    That trade is only sound if binding to the LAN is *deliberate*. Setting
    ``LOOTCODE_TRUST_LAN=1`` is how you say so; without it, a bind to 0.0.0.0 is
    far more likely to be a copied command line than a decision.
    """
    if _is_loopback(host) or settings.TRUST_LAN:
        return
    # Printed rather than only raised: uvicorn catches a lifespan exception and
    # wraps it in a traceback, which would bury the one thing the operator needs
    # to read.
    print(
        f"\n{'=' * 72}\n"
        f"REFUSING TO START — {settings.APP_NAME} would bind to {host!r}.\n\n"
        "That is reachable from your network, and this app has NO authentication:\n"
        "  * /admin/* can create and overwrite any problem in the bank\n"
        "  * POST /admin/verify executes arbitrary submitted Python\n"
        "  * the default `subprocess` sandbox does NOT block network access\n\n"
        "If you want that on a LAN you trust, say so explicitly:\n"
        f"    LOOTCODE_TRUST_LAN=1 uvicorn app.main:app --host {host}\n\n"
        "Otherwise bind to 127.0.0.1. See docs/security.md.\n"
        f"{'=' * 72}\n",
        file=sys.stderr, flush=True)
    raise SystemExit(
        f"refusing to bind to {host!r} without LOOTCODE_TRUST_LAN=1")


def main() -> None:
    import uvicorn

    # The lifespan checks this too, but failing before uvicorn prints its banner
    # makes the reason obvious.
    configure_logging()
    check_bind_is_intentional(settings.HOST)
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    main()
