"""Shared Jinja2 templates object with a markdown filter."""
from __future__ import annotations

import os

import markdown as _md
from fastapi.templating import Jinja2Templates

from .config import settings

templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


def _render_markdown(text: str | None) -> str:
    return _md.markdown(text or "", extensions=["fenced_code", "tables", "sane_lists"])


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
templates.env.globals["app_name"] = settings.APP_NAME
templates.env.globals["ai_enabled"] = settings.ai_enabled
templates.env.globals["static"] = _static_url
