"""Offline authoring tooling: it builds the bank, it does not serve it.

Nothing here is imported by the running web app. It was living in `app/` — 2.9k
lines of it, roughly a third of the runtime package's Python — which made the
runtime's dependency set and its Docker image bigger than they are, and made
the boundary between "code that answers a request" and "code an author runs at
a terminal" a matter of folklore.

The dependency points one way: `authoring/` imports from `app/` (the executor,
the LLM transport, the content loader), and `app/` never imports from here. A
new import of `authoring` inside `app` is a mistake.

- `hint_generator.py`  the hint generate -> judge -> regenerate quality gate,
                       with its prompt templates and judge exemplars. Driven by
                       `scripts/improve_hints.py`. See `docs/hint-generation.md`.

The *interactive* AI features stay in `app/llm/`: `help_generator.py` streams a
hint on the problem page, and `generator.py`/`fill_in.py` back the admin
"Generate with AI" flow. Those serve requests.
"""
