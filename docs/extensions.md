# Optional extensions

An **extension** is a feature that lives in its own top-level folder and can be
deleted without leaving a trace. If the folder is there, the feature exists and
is visible; if it is not, lootcode is exactly what it was before — no route, no
nav item, no import, no error.

Today there is one: `icf/`, the Industry Coding Framework (see
`icf/README.md`).

## Why

Some features are worth shipping without making everyone who clones the repo
carry them. `content/problems-extended/` already makes that argument for
problems; this makes it for code. The alternative — `if os.path.isdir("icf")`
sprinkled through `main.py` and `base.html` — is how a removable feature
becomes permanently welded in.

## The seam

Three things in core, none of which names a specific extension.

### 1. `app/extensions.py`

```python
OPTIONAL_EXTENSIONS = ("icf",)     # top-level packages to look for
```

`load_extensions(app)` runs once from `app/main.py`, right after the core
routers are included. For each name it tries `importlib.import_module(name)`:

* `ModuleNotFoundError` **for that package** → skipped silently. The folder is
  gone; that is the supported state.
* any other import failure → logged and re-raised. A *broken* extension is a
  bug, and swallowing it would leave the feature mysteriously missing.

The module must expose `register(app) -> ExtensionInfo`. What it does inside
is its own business: mount routers and static files, join the Jinja
environment, open its own database.

### 2. The registry

`ExtensionInfo` carries what core needs to know:

| Field | Used for |
|---|---|
| `name` | logging, and the `/extensions` roster in the registry |
| `nav` | `NavItem(label, href, title)` links rendered in the header (`base.html`) |
| `identity_roots` | URL roots that get a cookie identity (`app/main._wants_identity`) |

`identity_roots` is not cosmetic: an extension's pages extend `base.html`,
which reads `request.state.is_account`, so they need the same identity core's
own pages get. Core's list (`/problems`, `/api`, `/admin`, …) is deliberately
narrow so crawler traffic does not mint a user row per 404.

`REGISTRY` is a live object exported to Jinja as `extensions`, so
`{% for item in extensions.nav %}` renders nothing on a stock install.

### 3. `app/executor/sandbox.py`

The process-level half of the executor — rlimits, own process group, minimal
environment, throwaway workdir, kill-on-timeout — is one function,
`run_harness(harness_path, files, payload, limits, overall_s)`. Core's
`subprocess_executor` calls it, and so can an extension that needs to run
untrusted code with a different harness. There is one copy of the security
boundary, not one per feature. Any change to it goes through the
`executor-security-reviewer` subagent, exactly as before.

## Writing one

```python
# myfeature/__init__.py
from app.extensions import ExtensionInfo, NavItem

def register(app) -> ExtensionInfo:
    from app.templating import templates
    from .routers import pages

    templates.env.loader = ChoiceLoader([templates.env.loader,
                                         FileSystemLoader(TEMPLATES_DIR)])
    app.mount("/myfeature/static", StaticFiles(directory=STATIC_DIR))
    app.include_router(pages.router)
    return ExtensionInfo(name="myfeature",
                         nav=(NavItem(label="My Feature", href="/myfeature"),),
                         identity_roots=("/myfeature",))
```

Then add `"myfeature"` to `OPTIONAL_EXTENSIONS`, and to `_EXTENSION_DATABASES`
in the root `conftest.py` if it has a database of its own.

Rules that keep the arrow pointing one way:

* **Core never imports an extension.** The extension imports `app.*`; nothing
  in `app/` may import from it. (Same rule `authoring/` follows.)
* **Keep its state out of `lootcode.db`.** That file holds irreplaceable user
  data; a removable feature should not leave tables behind. `icf/` keeps its
  own SQLite file and references users by the cookie's id string.
* **Own your own templates, static files, content, scripts, tests and docs.**

## Tooling

Everything is existence-guarded, so each of these behaves identically with or
without the folder:

| | How |
|---|---|
| pytest | the root `conftest.py` appends `<ext>/tests` when it exists, and redirects the extension's database env var |
| `make test` | plain `pytest`, which picks that up |
| `make typecheck` | `mypy app authoring $(EXTENSIONS)` — `$(wildcard icf)` expands to nothing |
| ruff | linted automatically; per-file ignores live in `pyproject.toml` |
| `make check` | `check-bank` ends with `make icf-verify`, a no-op when absent |
| coverage | `source = ["app"]` is unchanged, so the gate does not move |

`tests/test_extensions.py` pins the contract, including a test that starts the
real app with the extension's import blocked and asserts the app cannot tell.
