# Product Requirements — lootcode

## 1. Vision

lootcode helps people get
better at programming by practicing real coding problems with instant,
test-based feedback and scoring.

## 2. Goals & non-goals

**Goals (v1)**
- Let a user solve a coding problem in-browser and get scored against tests.
- A clean, fast solving experience (editor with syntax highlighter, run, results)
- A content model that makes adding problems easy. 
- Let user browse available coding problems
- Problems will have difficulty level easy, medium and hard
- User can filter down to each category of difficulty
- Problems have topics (e.g. dynamic programming, greedy algorithms, sorting, search etc...) that user can filter down the
entire problem set bank to those topics.
- A canonical solution exists for the problem in the content model that passes all of the tests and requirements of the problem.
- supports python 3 language for V1

**Non-goals (v1)** — 🔲 confirm/trim
- Live contests / timed competitions.
- Discussion forums, social feed.
- Multiplayer / interviews.
- Mobile-native apps.
- support any other language other than Python3
- only correctness test for V1, will add efficiency tests e.g. time/memory later.

## 3. Target users

- Self-learners prepping for interviews

## 4. Core user stories (v1)

- As a visitor, I can browse/search problems by topic and difficulty.
- As a user, I can open a problem and read its statement, constraints, examples.
- As a user, I can write a solution in my chosen language (python only in v1) with starter code.
- As a user, I can **run** against the hidden tests and see how many tests passed/failed and total score.
- As a user, Once my solution passes all of the tests, I can see it among my solved problems.
- As a user, I can see my submission history and which problems I've solved.
- As an author/admin, I can add a new problem (statement, tests, starters).
- As an author/admin, I can ask an integrated cloud provide LLM service to create a new problem for me and fill it in, including tests 
- As an author/admin, I can provide a large text of many problems and LLM service that is integrated can use it as either directly create those problems or generate problems similar to those (e.g. same technique, but different name)


## 5. Scoring model

- **Weighted per test** — sum of passed test weights.

Also decide: do time/memory affect score, or just correctness? *Default:*
correctness only for v1; show time/memory for info.

## 6. Languages supported (v1)

Python

## 7. Success metrics

Nothing for V1 at the moment, just functioning application with large bank of problems and solutions.


## 8. Constraints & requirements

- Untrusted user code **must** run sandboxed — see `docs/code-execution.md`.
- p95 "run" latency target:  ≤ 10s for simple problems.
- Privacy: user code is private to the user; see `docs/security.md`.

## 9. Open questions

## 10. Out of scope for now

Anything not above. Park ideas in `docs/roadmap.md` under "Later / Someday".
