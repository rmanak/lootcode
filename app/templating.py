"""Shared Jinja2 templates object with a markdown filter."""
from __future__ import annotations

import os
from datetime import datetime, timezone, tzinfo

import markdown as _md
from fastapi.templating import Jinja2Templates

from .config import settings

templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


def _render_markdown(text: str | None) -> str:
    return _md.markdown(text or "", extensions=["fenced_code", "tables", "sane_lists"])


def _local_dt(dt: datetime | None, tz: tzinfo, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Render a stored UTC timestamp in the viewer's timezone.

    Submission `created_at` values are stored as UTC but come back from SQLite as
    naive datetimes, so we attach UTC before converting to `tz` (the visitor's
    zone from the `lc_tz` cookie; see `pages._user_tz`)."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz).strftime(fmt)


def _static_url(path: str) -> str:
    """Static asset URL with an mtime cache-buster (e.g. /static/app.css?v=1234).

    The query string changes whenever the file changes, so browsers re-fetch
    edited CSS/JS instead of serving a stale cached copy.
    """
    try:
        version = int(os.path.getmtime(settings.STATIC_DIR / path))
    except OSError:
        return f"/static/{path}"
    return f"/static/{path}?v={version}"


templates.env.filters["markdown"] = _render_markdown
templates.env.filters["localdt"] = _local_dt
templates.env.globals["app_name"] = settings.APP_NAME
templates.env.globals["static"] = _static_url
