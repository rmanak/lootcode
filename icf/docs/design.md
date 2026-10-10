# Why ICF is shaped this way

## It is an extension, not a feature branch

The requirement was that the whole thing be removable: present means visible,
absent means it never existed. That ruled out touching core in feature-shaped
ways. What core grew instead is three *generic* seams, described in
`docs/extensions.md`: a loader, a registry that feeds the nav and the identity
middleware, and one shared sandbox primitive. None of them names ICF.

## Its own database

`icf/data/icf.db`, not tables in `lootcode.db`. That file holds accounts,
submissions and solved history that exist nowhere else, and an optional
feature has no business adding tables to it — or orphaning them the day the
folder is deleted. Rows here reference a user by the id in the `lc_uid`
cookie, with no cross-file foreign key.

The cost is real and accepted: "My Progress" cannot join ICF results into the
core dashboard, so ICF carries its own history and report pages.

## Problems on disk, nothing seeded

A handful of definitions do not need a database, and a second copy is a second
thing to drift. `content.py` parses a directory and caches by newest mtime;
the case list is recovered by **parsing** `@case("…")` decorators with `ast`,
never by importing the module — the same static-only stance
`app/problem_spec.py` takes, for the same reason: this runs in the web
process.

## Tests as code, not as data

The core bank grades `(input, expected)` pairs, which is right for one
function with one answer. An ICF level is a *behaviour* — sequences, states,
"this must still be true afterwards" — and 40–80 of those per level is not
expressible as data without inventing a language. So a case is a Python
function that takes the solver's class, and the readable failure message it
produces is the thing the solver actually learns from.

The cost is that test modules run in the sandbox, which is why authoring stays
file-only — and why grading is split across two processes and two runs, so a
submission can neither read the tests nor write its own results
(`security.md`, and ADR 0003).

## Only a submit unlocks

*Run* is the fast loop: the current level's visible cases. *Submit* is the
real thing: levels 1…N, hidden included. Unlocking on a run would hand the
next level to someone who has not passed the hidden tests, which is what the
gate is for. Passing is sticky in the other direction — a later regression
shows in the results but never re-locks what was earned, because taking
progress away mid-attempt punishes exactly the refactoring the format is
asking for.

## The clock is the server's

`expires_at` is stored when the attempt starts; the browser only renders a
countdown from the `remaining_ms` it is handed and re-syncs. A run made after
the clock expires is still graded and still shown — the practice value is real
— but it is marked `late` and it never advances level state.

## An account is an object (and other shapes the problems teach)

Every shipped problem hinges on a data-model decision made at level 1 that
makes level 4 cheap or expensive:

- a field's optional expiry, so a backup is the same structure with remaining
  lifetimes (`in-memory-database`, and `chat-history` again);
- an account object the id merely points at, so merge-then-recreate needs no
  special case (`banking-system`);
- a recipe that *is* a list of versions, so rollback is an append
  (`recipe-manager`);
- assignments kept as records with a completed flag, so "active" and
  "overdue" are two halves of one predicate (`task-manager`);
- a task id that owns a timeline of snapshots, with a delete as one more
  snapshot, so the audit trail and "as of `time_at`" are lookups rather than
  replays (`task-board`);
- a session that carries its own rate, so a promotion never splits pay and
  double pay is one merged interval union (`worker-time-tracker`);
- a parked vehicle as a stay that owns its spots and the rate it arrived
  under, so a five-spot bus is the same record as a car and a price change
  needs no bookkeeping for vehicles already inside (`multi-level-parking-lot`);
- a meeting as an object whose room is just a field, so rescheduling it or
  rehousing it when its room closes keeps its id and booking order for free
  (`meeting-room-scheduler`);
- an owner on every item from level 1, so the unlimited `"admin"` needs no
  special case (`inventory-management`) — and the same shape again in the
  original CodeSignal wording, where a directory is only part of a name and a
  compressed file is decompressed under its own name (`cloud-storage`).

That is the thing the
format is actually testing, and the level statements are written so the
lesson is available without being handed over.
