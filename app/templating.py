"""Shared Jinja2 templates object with a markdown filter."""
from __future__ import annotations

import os
from datetime import UTC, datetime, tzinfo

import markdown as _md
from fastapi.templating import Jinja2Templates

from .config import settings
from .extensions import REGISTRY

templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


_MD_EXTENSIONS = ["fenced_code", "tables", "sane_lists", "pymdownx.arithmatex"]
_MD_CONFIG = {
    # `generic` emits <span class="arithmatex">\(…\)</span> (inline) and
    # <div class="arithmatex">\[…\]</div> (display) for static/math.js to hand to
    # KaTeX, instead of MathJax <script> tags. The math is lifted out before
    # Markdown runs, so `_`, `*` and `\{` inside a formula survive intact, and
    # its text is HTML-escaped. `smart_dollar` (the default) only pairs a `$`
    # that hugs its content, so prose like "buy for $1, sell for $9" stays text.
    # See docs/math-in-statements.md.
    "pymdownx.arithmatex": {"generic": True, "smart_dollar": True},
}


def render_markdown(text: str | None) -> str:
    """Render statement Markdown to HTML, with math lifted out for KaTeX."""
    return _md.markdown(text or "", extensions=_MD_EXTENSIONS,
                        extension_configs=_MD_CONFIG)


def _local_dt(dt: datetime | None, tz: tzinfo, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Render a stored UTC timestamp in the viewer's timezone.

    Submission `created_at` values are stored as UTC but come back from SQLite as
    naive datetimes, so we attach UTC before converting to `tz` (the visitor's
    zone from the `lc_tz` cookie; see `pages._user_tz`)."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
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


templates.env.filters["markdown"] = render_markdown
templates.env.filters["localdt"] = _local_dt
templates.env.globals["app_name"] = settings.APP_NAME
# Live object, not a snapshot: extensions register during startup, after this
# module is imported. `extensions.nav` is empty on a stock install, and the
# header then renders exactly the links it always did.
templates.env.globals["extensions"] = REGISTRY
templates.env.globals["static"] = _static_url
