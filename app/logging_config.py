"""Application logging.

Before this existed there was exactly one logger in 8,346 lines of ``app/``
(``store.py``), used at one site, with no ``basicConfig`` anywhere — so its
records went to the root logger's last-resort handler and its ``debug``/``info``
calls went nowhere at all. Anything that failed quietly failed invisibly.

``configure_logging`` is called once from the lifespan, before the first request.
It is deliberately small: stdlib only, one stream handler, no file rotation. On a
home/LAN box the process is run by uvicorn or docker, and both already capture
stdout.

Two things are worth naming:

* **Uvicorn's own loggers are left alone.** It configures ``uvicorn.access`` and
  ``uvicorn.error`` itself; re-parenting them here produces either duplicated
  lines or silence depending on start order.
* **``audit`` is a separate logger** (``lootcode.audit``). ``/admin`` is
  unauthenticated by design on a LAN instance (see docs/security.md), so an
  admin write is the one event that must always leave a trace, regardless of
  what LOG_LEVEL the rest of the app is running at.
"""
from __future__ import annotations

import logging
import os
import sys

#: Every module logs through a child of this, so one line changes the whole app.
ROOT = "lootcode"

#: The audit trail for writes to the problem bank. Always at INFO or lower.
AUDIT = f"{ROOT}.audit"

_FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

_configured = False


def configure_logging(level: str | None = None) -> None:
    """Attach a stream handler to the ``lootcode`` logger. Idempotent.

    ``level`` defaults to ``$LOG_LEVEL`` and then to INFO. An unrecognized value
    falls back to INFO rather than raising — a typo in an env var should not stop
    the server from starting.
    """
    global _configured
    if _configured:
        return

    name = (level or os.environ.get("LOG_LEVEL") or "INFO").strip().upper()
    resolved = getattr(logging, name, None)
    if not isinstance(resolved, int):
        resolved = logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT))

    root = logging.getLogger(ROOT)
    root.setLevel(resolved)
    root.handlers[:] = [handler]
    # Don't hand records to the real root logger as well; uvicorn attaches its
    # own handler there and every line would print twice.
    root.propagate = False

    # The audit trail is never quieter than INFO, whatever LOG_LEVEL says.
    logging.getLogger(AUDIT).setLevel(min(resolved, logging.INFO))

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """A logger under the app's namespace. Pass ``__name__``.

    ``app.routers.admin`` becomes ``lootcode.routers.admin``, so the whole app is
    one subtree and a single ``logging.getLogger("lootcode")`` call reconfigures
    it.
    """
    suffix = name.removeprefix("app.").removeprefix("app")
    return logging.getLogger(f"{ROOT}.{suffix}" if suffix else ROOT)


def audit(message: str, *args) -> None:
    """Record a write to the problem bank.

    Separate from ordinary logging on purpose: these routes are unauthenticated
    on a LAN instance, so this is the only record of who changed what.
    """
    logging.getLogger(AUDIT).info(message, *args)
