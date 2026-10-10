# AI solution analysis ("✨ Analysis")

The **✨ Analysis** button at the right end of the problem page's Run & Score
row asks the optional LLM endpoint for a review of the code currently in the
editor, modelled on LeetCode's Analysis panel. The report has three pillars:

| Pillar | What it shows |
|--------|---------------|
| **Approach** | *Current* technique(s) the code really uses vs. the *Suggested* best ones; the **Key Idea** of the suggested approach; one Socratic **Consider** question (aimed at the root cause when the run failed, at a variation when it passed). |
| **Efficiency** | *Time* and *Space* tabs, each with current vs. suggested Big-O and a concrete suggestion. |
| **Code Style** | **Readability** and **Structure** ratings (Excellent / Good / Fair / Poor) and a suggestion that names the student's identifiers. |

Above them is a pillar checklist that ticks off as each part is written, the
verdict (`Accepted · 12/12 tests`), and a one-line encouraging summary keyed to
that verdict. The report renders between the Run & Score row and the test
results, and closes with ×.

It uses the same endpoint as "Get More Help with AI" ([ai-help.md](ai-help.md)):
the button is enabled exactly when `settings.llm_help_available` is, and both
switch on and off live as the LLM server comes and goes (see "Following the LLM
server up and down" there). Disabled, it takes the same grey as the help button.

## How it works

1. `app/static/analysis.js` POSTs the editor's code to
   `POST /api/problems/{slug}/analyze` (`app/routers/submissions.py`).
2. The route **grades the code** through the same `run_submission` path as
   `/run`, so the model is told the real verdict rather than guessing it.
   Nothing is recorded: an analysis is not an attempt. Empty code, the untouched
   starter, and anything over `MAX_ANALYSIS_CODE_CHARS` are rejected with 400.
3. `app/llm/solution_analyzer.py` builds the prompt (`analysis_prompt.txt`)
   and streams the model's answer as Server-Sent Events:
   `status` → `verdict` → `progress {chars, pillars}` … → `result {analysis}` →
   `done`, or a terminal `error`.
4. `parse_analysis` normalises the answer into the shape the page renders.

## The prompt

`app/llm/analysis_prompt.txt` (literal-token templating, like the other
prompts) gives the model:

- the title, statement and required signature;
- the problem's **canonical solution as a private reference**, so "suggested"
  is calibrated for custom problems too. The prompt forbids quoting it, and
  every prose field is length-capped by the schema, which limits what a student
  could coax out of it;
- the student's code, fenced and marked as data, never instructions;
- the verdict from `build_verdict`: status, counts by failure kind, and the
  **first failing visible test's** input / expected / returned value or error.
  **Hidden tests contribute only counts** — never inputs, expected values or
  outputs;
- field-by-field rules (label sets, word limits, the rating rubric,
  amortised-complexity and "Wrong Answer is not slowness" guards), and
- two worked examples built from LeetCode's own Analysis of *Meeting Rooms
  Required* — a correct min-heap solution and a wrong stack-based one.

## Hardening

The code under analysis is untrusted, and so is everything it can influence. A
submission can rewrite its own `result.json` on exit, so every field of a
result (status, error, returned value) is attacker-controlled.

- **Single-pass templating.** `render_prompt` substitutes tokens in the
  template only, never inside a value. With chained `.replace` calls,
  `{{CODE}}` in an exception message got expanded into a full copy of the
  submission each time: a 20 KB request rendered a 3 MB prompt.
- **Random code fence** per request (`STUDENT_CODE_<hex>`), so code cannot close
  it early and smuggle in instructions.
- **Bounded verdict.** Unknown statuses become "error", every value is clipped,
  and hidden cases are excluded from the name lookup even if a name collides.
- **Size limits.** The 20,000-character code cap is applied *after*
  `expandtabs`, and any prompt over `MAX_PROMPT_CHARS` (60,000) is refused.
- **Concurrency.** At most 2 analyses run at once; any more get an error frame
  telling the user to retry.
- **No internal details reach the page.** Grading failures send a fixed message
  and the details go to the log.
- **The canonical is in the prompt.** This is the one open trade-off; see the
  threat table in [security.md](security.md).

## Structured output

The answer is constrained by `ANALYSIS_SCHEMA` (`response_format: json_schema`,
which llama.cpp compiles to a grammar):

- **Approach labels** are an enum: the 44 canonical tags (`app/tags.py`)
  rendered for reading (`heap` → "Heap (Priority Queue)") plus the
  analysis-only label **"Brute Force"**. Without it, the grammar forced a model
  that had begun writing "Brute Force" into the nearest legal label, and a
  nested-loop Two Sum came back as "Breadth-First Search". It is a label for a
  *solution*, not a problem tag, so it is not in the tag vocabulary.
- **Ratings** are an enum; every prose field has a `maxLength`.
- **Key order is generation order.** The summary is generated *last*, after
  the model has worked through the code, even though the page shows it first.
  The fixed order is also what lets the route tick pillars off mid-stream
  (`pillars_done`).

If an endpoint rejects `json_schema`, the call degrades to `json_object` and
then to a prompt-only call (`client.response_formats`). `parse_analysis`
then folds labels onto the canonical set, ratings onto the scale, and stray
LaTeX in a complexity (`$O(n \log n)$`) into plain `O(n log n)`. The page
typesets that as math: italic variables, superscript exponents.

## Speed and thinking

Thinking is **off** (`chat_template_kwargs.enable_thinking: false`), as for AI
help. With Qwen3.8-27B (Q5, RTX 3090 Ti) a report takes about 11–13 s: about
2.5 s to the first token, plus grading time. A trial with thinking on
returned no JSON content at all within a 4,000-token budget, which rules it
out for a button. The schema plus the explicit rubric gives good non-thinking
answers.

## Tuning

Edit `analysis_prompt.txt`. Keep the two worked examples consistent with the
rules above them, because the model copies examples more faithfully than it
follows rules. If you change the field set, change `ANALYSIS_SCHEMA`,
`parse_analysis` and `render` in `analysis.js` together. `tests/test_analysis.py`
pins the route, the verdict's hidden-test boundary, the schema and the
normaliser, with the model stubbed.
