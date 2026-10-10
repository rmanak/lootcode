"""Optional feature packages, loaded at startup if they happen to be installed.

An *extension* is a top-level package (a folder at the repo root) that the app
looks for by name and, when it is there, lets register itself: routers, its own
static mount, its own templates, a nav entry. When it is **not** there the app
is exactly what it was before — no route, no nav item, no import, no error.
That is the whole contract, and it is deliberately one-way: core never imports
an extension, and nothing in core is named after one.

Why this exists rather than just adding the feature to ``app/``: some features
are worth shipping without making everyone who clones the repo carry them (the
same argument ``content/problems-extended/`` already makes for problems). The
alternative — ``if os.path.isdir("icf"):`` sprinkled through ``main.py`` and
``base.html`` — is how a "removable" feature becomes permanently welded in.

The seam is three things:

* this loader, called once from the lifespan;
* :data:`REGISTRY`, which templates read for their nav (empty renders nothing);
* :attr:`ExtensionInfo.identity_roots`, so an extension's pages get the same
  cookie identity core's own pages do (see ``app.main._wants_identity``).

An extension declares itself with a module-level ``register(app)`` returning an
:class:`ExtensionInfo`.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field

from .logging_config import get_logger

log = get_logger(__name__)

#: Top-level packages to look for. A name here is an *offer*, not a dependency:
#: if the folder is not on disk, startup skips it silently.
OPTIONAL_EXTENSIONS: tuple[str, ...] = ("icf",)


@dataclass(frozen=True)
class NavItem:
    """One link in the site header, contributed by an extension."""

    label: str
    href: str
    title: str = ""


@dataclass(frozen=True)
class ExtensionInfo:
    """What an extension tells core about itself, returned by ``register(app)``.

    ``identity_roots`` are URL path roots that should get a cookie identity —
    the extension's equivalent of ``app.main._IDENTITY_ROOTS``. Without it the
    extension's pages render with no ``request.state.user_id`` and ``base.html``
    raises on ``request.state.is_account``.
    """

    name: str
    nav: tuple[NavItem, ...] = ()
    identity_roots: tuple[str, ...] = ()


@dataclass
class Registry:
    """Everything loaded extensions have contributed. Empty = stock lootcode."""

    loaded: list[ExtensionInfo] = field(default_factory=list)

    @property
    def names(self) -> list[str]:
        return [e.name for e in self.loaded]

    @property
    def nav(self) -> list[NavItem]:
        return [item for e in self.loaded for item in e.nav]

    @property
    def identity_roots(self) -> tuple[str, ...]:
        return tuple(root for e in self.loaded for root in e.identity_roots)

    def add(self, info: ExtensionInfo) -> None:
        self.loaded.append(info)

    def clear(self) -> None:
        self.loaded.clear()


#: Process-wide, and read live by the Jinja environment (see app/templating.py),
#: so a template picks up whatever was registered at startup.
REGISTRY = Registry()


def _is_absent(exc: ImportError, name: str) -> bool:
    """Whether ``exc`` means "that package isn't installed" and nothing worse.

    The distinction matters: a missing *extension* is the supported state and
    must be silent, but an extension that fails to import its own dependency is
    a bug, and swallowing it would leave the feature mysteriously missing.
    """
    return isinstance(exc, ModuleNotFoundError) and exc.name == name


def load_extensions(app, names: tuple[str, ...] = OPTIONAL_EXTENSIONS,
                    registry: Registry = REGISTRY) -> list[ExtensionInfo]:
    """Import each optional package and let it register itself against ``app``.

    Returns what loaded, in order. Absent packages are skipped; every other
    failure is raised, because it is a broken extension rather than a missing
    one.
    """
    for name in names:
        try:
            module = importlib.import_module(name)
        except ImportError as exc:
            if _is_absent(exc, name):
                log.debug("optional extension %r not installed — skipping", name)
                continue
            raise
        register = getattr(module, "register", None)
        if register is None:
            raise RuntimeError(
                f"optional extension {name!r} has no register(app) function")
        info = register(app)
        if not isinstance(info, ExtensionInfo):
            raise RuntimeError(
                f"{name}.register(app) must return an ExtensionInfo, got {info!r}")
        registry.add(info)
        log.info("loaded extension %r (nav: %s)", info.name,
                 ", ".join(i.href for i in info.nav) or "none")
    return list(registry.loaded)
