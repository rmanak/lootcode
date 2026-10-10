// ICF workspace: level tabs, the clock, run/submit, autosave.
//
// Deliberately plain: one file, no build step, and it reuses core's CodeMirror
// bundle (window.LootEditor) rather than shipping a second editor.
(function () {
  const boot = document.getElementById("icf-bootstrap");
  if (!boot) return;
  const DATA = JSON.parse(boot.textContent);

  const editorEl = document.getElementById("icf-code");
  const editor = LootEditor.create(editorEl);

  const runBtn = document.getElementById("icf-run");
  const submitBtn = document.getElementById("icf-submit");
  const submitLevelEl = document.getElementById("icf-submit-level");
  const statusEl = document.getElementById("icf-status");
  const resultsEl = document.getElementById("icf-results");
  const savedEl = document.getElementById("icf-saved");
  const clockEl = document.getElementById("icf-clock");
  const clockTimeEl = document.getElementById("icf-clock-time");
  const finishBtn = document.getElementById("icf-finish");

  // --- resizing ------------------------------------------------------------
  // Core's app.js wires these handles on the normal problem page, but it only
  // runs there, so the workspace does its own (same behaviour).
  function dragHandle(handle, onStart, onMove) {
    if (!handle) return;
    const onUp = (e) => {
      handle.classList.remove("dragging");
      handle.releasePointerCapture(e.pointerId);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
    handle.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      onStart(e);
      handle.classList.add("dragging");
      handle.setPointerCapture(e.pointerId);
      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp);
    });
  }

  // The strip below the editor: taller/shorter.
  let startY = 0, startH = 0;
  dragHandle(document.querySelector(".icf-workbench .editor-resize"),
    (e) => { startY = e.clientY; startH = editor.height(); },
    (e) => { editor.setHeight(Math.max(160, startH + (e.clientY - startY))); });

  // The gutter between the statement and the editor: rebalance the split.
  const solveEl = document.querySelector(".icf-solve");
  dragHandle(document.querySelector(".icf-gutter"), () => {}, (e) => {
    const rect = solveEl.getBoundingClientRect();
    const min = rect.width * 0.2, max = rect.width * 0.8;
    const left = Math.min(max, Math.max(min, e.clientX - rect.left));
    solveEl.style.setProperty("--split", left + "px");
    editor.refresh();
  });

  let attempt = DATA.attempt;         // null until an attempt is started
  let currentLevel = attempt ? highestUnlocked(attempt) : 1;

  function highestUnlocked(state) {
    let best = 1;
    state.levels.forEach((l) => { if (l.unlocked) best = Math.max(best, l.level); });
    return best;
  }
  function levelState(n) {
    if (attempt) return attempt.levels.find((l) => l.level === n);
    // No attempt yet: level 1 is what the Start button opens, and nothing is
    // passed. Returning a shape rather than null keeps the pills honest.
    return { level: n, unlocked: n === 1, passed: false };
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  // --- starting an attempt -------------------------------------------------
  async function start(mode) {
    const btns = [document.getElementById("icf-start-exam"),
                  document.getElementById("icf-start-practice")].filter(Boolean);
    btns.forEach((b) => { b.disabled = true; });
    try {
      const resp = await fetch(`/api/icf/${DATA.slug}/attempts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: mode }),
      });
      if (!resp.ok) throw new Error(`Could not start: HTTP ${resp.status}`);
      // Reload so the page renders in its "attempt in progress" state from the
      // server, rather than this script rebuilding half the DOM by hand.
      location.reload();
    } catch (err) {
      btns.forEach((b) => { b.disabled = false; });
      alert(err.message);
    }
  }
  const startExam = document.getElementById("icf-start-exam");
  const startPractice = document.getElementById("icf-start-practice");
  if (startExam) startExam.addEventListener("click", () => start("exam"));
  if (startPractice) startPractice.addEventListener("click", () => start("practice"));

  // --- level tabs ----------------------------------------------------------
  const tabs = Array.from(document.querySelectorAll(".icf-tab"));
  const panels = Array.from(document.querySelectorAll(".icf-panel"));

  function showPanel(name) {
    tabs.forEach((t) => t.classList.toggle("is-active", t.dataset.panel === name));
    panels.forEach((p) => { p.hidden = p.dataset.panelView !== name; });
  }
  function selectLevel(n) {
    const state = levelState(n);
    if (attempt && state && !state.unlocked) {
      // A locked level is still readable as a *tab*, but it can't become the
      // target of Run/Submit — otherwise the gate is decoration.
      showPanel("level" + n);
      paintTabs();
      return;
    }
    currentLevel = n;
    showPanel("level" + n);
    if (submitLevelEl) submitLevelEl.textContent = String(n);
    paintTabs();
  }
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      if (tab.dataset.level) selectLevel(Number(tab.dataset.level));
      else showPanel(tab.dataset.panel);
    });
  });
  // The tabs carry the level state now: locked, passed, and which one the
  // Run/Submit buttons are pointed at.
  function paintTabs() {
    tabs.forEach((tab) => {
      if (!tab.dataset.level) return;
      const n = Number(tab.dataset.level);
      const state = levelState(n);
      tab.classList.toggle("is-locked", !(state && state.unlocked));
      tab.classList.toggle("is-passed", !!(state && state.passed));
    });
  }

  // --- the clock -----------------------------------------------------------
  // The server owns the deadline; this only renders the countdown from the
  // remaining_ms it was handed, and re-syncs periodically so a sleeping laptop
  // (or a fiddled system clock) can't buy extra time.
  let deadline = null;
  function setClock(state) {
    if (!clockEl) return;
    if (!state) {                       // nothing started: no clock at all
      clockEl.hidden = true;
      deadline = null;
      return;
    }
    if (state.remaining_ms === null || state.remaining_ms === undefined) {
      clockEl.hidden = false;           // practice: say so instead of counting
      clockEl.className = "icf-clock";
      clockTimeEl.textContent = "practice";
      deadline = null;
      return;
    }
    clockEl.hidden = false;
    deadline = Date.now() + state.remaining_ms;
    tick();
  }
  function tick() {
    if (deadline === null) return;
    const left = Math.max(0, deadline - Date.now());
    const total = Math.floor(left / 1000);
    const mm = String(Math.floor(total / 60)).padStart(2, "0");
    const ss = String(total % 60).padStart(2, "0");
    clockTimeEl.textContent = `${mm}:${ss}`;
    clockEl.className = "icf-clock" +
      (left === 0 ? " over" : left < 5 * 60000 ? " danger"
        : left < 15 * 60000 ? " warn" : "");
    if (left === 0) clockTimeEl.textContent = "time up";
  }
  setInterval(tick, 1000);

  async function resync() {
    if (!attempt) return;
    try {
      const resp = await fetch(`/api/icf/attempts/${attempt.id}`);
      if (!resp.ok) return;
      const data = await resp.json();
      applyState(data.attempt);
    } catch (e) { /* offline: keep counting down locally */ }
  }
  setInterval(resync, 60000);

  function applyState(state) {
    attempt = state;
    setClock(state);
    paintTabs();
    if (state.status !== "active") {
      if (runBtn) runBtn.title = "This attempt has ended — runs are recorded but no longer unlock levels.";
    }
  }

  // --- autosave ------------------------------------------------------------
  let saveTimer = null;
  function scheduleSave() {
    if (!attempt) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(save, 2500);
  }
  async function save() {
    if (!attempt) return;
    try {
      await fetch(`/api/icf/attempts/${attempt.id}/draft`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: editor.getValue() }),
      });
      if (savedEl) {
        savedEl.textContent = "saved";
        setTimeout(() => { savedEl.textContent = ""; }, 1800);
      }
    } catch (e) { if (savedEl) savedEl.textContent = "not saved"; }
  }
  // CodeMirror hides the textarea and edits a contenteditable of its own, so
  // the events come from the view's DOM node, not from `editorEl`.
  editor.view.dom.addEventListener("input", scheduleSave);
  editor.view.dom.addEventListener("keyup", scheduleSave);
  window.addEventListener("beforeunload", () => {
    if (attempt && navigator.sendBeacon) {
      navigator.sendBeacon(`/api/icf/attempts/${attempt.id}/draft`,
        new Blob([JSON.stringify({ code: editor.getValue() })],
                 { type: "application/json" }));
    }
  });

  // --- running -------------------------------------------------------------
  async function grade(kind) {
    if (!attempt) return;
    const state = levelState(currentLevel);
    if (state && !state.unlocked) {
      statusEl.textContent = `Level ${currentLevel} is locked.`;
      return;
    }
    runBtn.disabled = submitBtn.disabled = true;
    statusEl.textContent = kind === "submit"
      ? `Submitting level ${currentLevel} — running levels 1–${currentLevel}, hidden tests included…`
      : `Running level ${currentLevel} visible tests…`;
    resultsEl.innerHTML = "";
    try {
      const resp = await fetch(`/api/icf/attempts/${attempt.id}/${kind}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level: currentLevel, code: editor.getValue() }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || `HTTP ${resp.status}`);
      applyState(data.attempt);
      render(data);
      statusEl.textContent = "";
    } catch (err) {
      resultsEl.innerHTML = `<div class="icf-loaderr">${esc(err.message)}</div>`;
      statusEl.textContent = "";
    } finally {
      runBtn.disabled = submitBtn.disabled = false;
    }
  }
  runBtn.addEventListener("click", () => grade("run"));
  submitBtn.addEventListener("click", () => grade("submit"));
  if (finishBtn) {
    finishBtn.addEventListener("click", async () => {
      if (!attempt || !confirm("End this attempt? The clock stops and it becomes read-only.")) return;
      await fetch(`/api/icf/attempts/${attempt.id}/finish`, { method: "POST" });
      location.href = `/icf/attempts/${attempt.id}`;
    });
  }

  // --- rendering results ---------------------------------------------------
  function render(data) {
    const run = data.run;
    const ok = run.all_passed;
    const parts = [];

    if (data.late) {
      parts.push('<div class="icf-late">⏱ Time is up — this run was recorded, ' +
        "but it no longer unlocks levels. Open the report to see how far you got.</div>");
    }
    parts.push(
      `<div class="icf-runhead ${ok ? "ok" : "no"}">` +
      `<strong>${run.passed_count}/${run.total_count}</strong> tests passed` +
      `<span>${data.mode === "submit" ? `levels 1–${data.level}` : `level ${data.level}, visible only`}</span>` +
      `<span>${Math.round(run.runtime_ms)} ms</span>` +
      (data.unlocked_level
        ? `<span class="icf-unlocked">🔓 Level ${data.unlocked_level} unlocked</span>`
        : "") +
      "</div>");

    if (run.load_error) {
      parts.push(`<div class="icf-loaderr">${esc(run.load_error)}</div>`);
    }

    run.levels.forEach((lv) => {
      const tally = `${lv.passed_count}/${lv.total_count}`;
      const cases = lv.cases.map((c) => {
        const cls = c.passed ? "pass"
          : c.status === "timeout" ? "timeout"
          : c.status === "error" ? "error" : "fail";
        const bits = [
          `<div class="icf-case ${cls}${c.hidden ? " hidden-case" : ""}">`,
          '<span class="dot"></span>',
          `<span class="label">${esc(c.label)}</span>`,
          `<span class="t">${c.hidden ? (c.passed ? "passed" : c.status) : Math.round(c.time_ms) + " ms"}</span>`,
        ];
        if (!c.hidden && c.message) {
          bits.push(`<pre class="${c.status === "failed" ? "" : "err"}">${esc(c.message)}</pre>`);
        }
        if (!c.hidden && c.stdout) {
          bits.push(`<button type="button" class="icf-out-toggle">▸ stdout</button>`,
                    `<pre hidden>${esc(c.stdout)}</pre>`);
        }
        bits.push("</div>");
        return bits.join("");
      }).join("");
      parts.push(
        `<div class="icf-levelblock"><h3>Level ${lv.level} — ${esc(lv.title)}` +
        `<span class="tally ${lv.all_passed ? "ok" : "no"}">${tally}</span></h3>` +
        `<div class="icf-cases">${cases}</div></div>`);
    });

    resultsEl.innerHTML = parts.join("");
    resultsEl.querySelectorAll(".icf-out-toggle").forEach((btn) => {
      btn.addEventListener("click", () => {
        const pre = btn.nextElementSibling;
        pre.hidden = !pre.hidden;
        btn.textContent = pre.hidden ? "▸ stdout" : "▾ stdout";
      });
    });
  }

  // --- boot ----------------------------------------------------------------
  if (attempt) {
    applyState(attempt);
    selectLevel(currentLevel);
  } else {
    // Nothing has started: open on the scenario, which is what a first-time
    // reader needs before the level requirements make sense. Run and Submit
    // are disabled server-side until there is an attempt to record against.
    showPanel("overview");
    paintTabs();
    if (submitLevelEl) submitLevelEl.textContent = "1";
  }
})();
