"""FastAPI application: server-rendered UI + JSON run API.

Run locally:   uvicorn app.main:app --reload
Or:            python -m app.main      (honours HOST/PORT from .env)
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select

from .config import settings
from .db import SessionLocal, init_db
from .models import Problem, User
from .routers import admin, pages, submissions
from .store import seed_collections, seed_from_content

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    with SessionLocal() as db:
        if not db.scalar(select(func.count()).select_from(Problem)):
            seed_from_content(db)
        # Curated lists are cheap to rebuild and idempotent, so (re)seed them on
        # every startup — a manifest edit takes effect on restart without a full
        # problem re-seed. Unknown slugs are logged, not fatal (see store).
        seed_collections(db)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")


@app.middleware("http")
async def attach_user(request: Request, call_next):
    """Give every visitor a cookie-based identity (no passwords). Skips static
    assets so a fresh visit creates exactly one guest user."""
    path = request.url.path
    if path.startswith("/static") or path == "/favicon.ico":
        return await call_next(request)

    uid = request.cookies.get("lc_uid")
    is_new = False
    with SessionLocal() as db:
        user = db.get(User, uid) if uid else None
        if user is None:
            user = User(name="guest")
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new = True
        request.state.user_id = user.id
        request.state.user_name = user.name
        # V2: templates show login vs account state from these (see base.html).
        request.state.is_account = user.is_account
        request.state.username = user.username
        uid = user.id

    response = await call_next(request)
    if is_new:
        response.set_cookie("lc_uid", uid, max_age=63_072_000,
                            httponly=True, samesite="lax")
    return response


app.include_router(pages.router)
app.include_router(submissions.router)
app.include_router(admin.router)


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    main()
