// Problem page: CodeMirror editor + Run & Score.
(function () {
  const root = document.querySelector(".solve");
  if (!root) return;

  const slug = root.dataset.slug;
  const difficulty = root.dataset.difficulty;
  const editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: "python",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false, // always indent with spaces — avoids Python TabError
    matchBrackets: true,
    extraKeys: {
      // Tab inserts spaces (or indents the selection); Shift-Tab unindents.
      Tab: (cm) =>
        cm.somethingSelected()
          ? cm.indentSelection("add")
          : cm.execCommand("insertSoftTab"),
      "Shift-Tab": (cm) => cm.indentSelection("subtract"),
    },
  });

  const btn = document.getElementById("run-btn");
  const statusEl = document.getElementById("status");
  const results = document.getElementById("results");

  btn.addEventListener("click", run);

  // Drag the strip below the editor to make it taller/shorter.
  const vHandle = document.querySelector(".editor-resize");
  if (vHandle) {
    let startY = 0, startH = 0;
    const onMove = (e) => {
      const h = Math.max(160, startH + (e.clientY - startY));
      editor.setSize(null, h);
    };
    const onUp = (e) => {
      vHandle.classList.remove("dragging");
      vHandle.releasePointerCapture(e.pointerId);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
    vHandle.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      startY = e.clientY;
      startH = editor.getWrapperElement().offsetHeight;
      vHandle.classList.add("dragging");
      vHandle.setPointerCapture(e.pointerId);
      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp);
    });
  }

  // Drag the gutter between the statement and the editor to rebalance the split.
  const gutter = document.querySelector(".col-gutter");
  if (gutter) {
    const onMove = (e) => {
      const rect = root.getBoundingClientRect();
      const min = rect.width * 0.2, max = rect.width * 0.8;
      const left = Math.min(max, Math.max(min, e.clientX - rect.left));
      root.style.setProperty("--split", left + "px");
      editor.refresh();
    };
    const onUp = (e) => {
      gutter.classList.remove("dragging");
      gutter.releasePointerCapture(e.pointerId);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
    gutter.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      gutter.classList.add("dragging");
      gutter.setPointerCapture(e.pointerId);
      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp);
    });
  }

  // "Mark as known" toggle: marking flips the control to a "Next problem" link
  // and lights the blue badge; clicking the badge unmarks it again. Both states
  // are in the DOM at once — we just toggle the `is-known` class.
  const knownCtl = document.getElementById("known-control");
  const knownBadge = document.getElementById("known-badge");
  if (knownCtl && knownBadge) {
    const markBtn = knownCtl.querySelector(".known-btn");
    async function setKnown(state) {
      try {
        const resp = await fetch(`/api/problems/${slug}/known`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ known: state }),
        });
        if (!resp.ok) return;
        const d = await resp.json();
        knownCtl.classList.toggle("is-known", d.known);
        knownBadge.hidden = !d.known;
      } catch (_) {
        /* offline / transient — leave the UI as-is */
      }
    }
    markBtn.addEventListener("click", () => setKnown(true));
    knownBadge.addEventListener("click", () => setKnown(false));
  }

  async function run() {
    btn.disabled = true;
    statusEl.textContent = "Running…";
    results.innerHTML = "";
    try {
      const resp = await fetch(`/api/problems/${slug}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: editor.getValue() }),
      });
      if (!resp.ok) {
        const e = await resp.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(e.detail || "Request failed");
      }
      render(await resp.json());
    } catch (err) {
      results.innerHTML = `<div class="run-error">${esc(err.message)}</div>`;
    } finally {
      btn.disabled = false;
      statusEl.textContent = "";
    }
  }

  function render(d) {
    // When solved, offer a jump to a random unsolved problem of the same
    // difficulty. /random/{difficulty} excludes solved problems (including the
    // one just solved), so it never sends the user back here.
    const next = d.solved
      ? `<a class="next-btn" href="/random/${encodeURIComponent(difficulty)}">Next ${esc(difficulty)} problem →</a>`
      : "";
    const summary = `<div class="summary ${d.solved ? "ok" : "no"}">
      <strong>${d.solved ? "All tests passed! 🎉" : `Passed ${d.passed_count} / ${d.total_count}`}</strong>
      <span>Score ${d.score}/${d.points}</span>
      <span>${d.runtime_ms} ms</span>${next}</div>`;

    const cases = d.results.map((r) => {
      const cls = r.passed ? "pass" : r.status === "timeout" ? "timeout" : "fail";
      let detail = "";
      if (!r.hidden) {
        if (r.error) detail += `<pre class="err">${esc(r.error)}</pre>`;
        if (r.stdout) detail += `<pre class="out">${esc(r.stdout)}</pre>`;
      }
      const t = r.time_ms != null ? ` <span class="t">${r.time_ms} ms</span>` : "";
      return `<div class="case ${cls}">
        <span class="dot"></span>
        <span class="label">${esc(r.label)}</span>
        <span class="st">${r.passed ? "passed" : esc(r.status)}</span>${t}
        ${detail}</div>`;
    }).join("");

    results.innerHTML = summary + `<div class="cases">${cases}</div>`;
  }

  function esc(s) {
    return (s || "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
})();
