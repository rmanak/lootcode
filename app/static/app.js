// Problem page: CodeMirror editor + Run & Score.
(function () {
  const root = document.querySelector(".solve");
  if (!root) return;

  const slug = root.dataset.slug;
  const difficulty = root.dataset.difficulty;
  // CodeMirror 6 editor, bundled in static/vendor/cm6.js as window.LootEditor:
  // Python syntax, context-aware auto-indent, 4-space Tab/Shift-Tab, and the
  // vertical indentation guides. Height comes from CSS (.editor-wrap .cm-editor).
  const editor = LootEditor.create(document.getElementById("code"));

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
      editor.setHeight(h);
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
      startH = editor.height();
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

  // "Visit later" toggle: an independent bookmark. Clicking the button (or the
  // title badge) flips state; `is-later` swaps the button's label and shows the
  // badge. Unlike "known" it has no "next problem" jump — it just stays flagged.
  const laterCtl = document.getElementById("later-control");
  const laterBadge = document.getElementById("later-badge");
  if (laterCtl && laterBadge) {
    const laterBtn = laterCtl.querySelector(".later-btn");
    async function setVisitLater(state) {
      try {
        const resp = await fetch(`/api/problems/${slug}/visit-later`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ visit_later: state }),
        });
        if (!resp.ok) return;
        const d = await resp.json();
        laterCtl.classList.toggle("is-later", d.visit_later);
        laterBadge.hidden = !d.visit_later;
      } catch (_) {
        /* offline / transient — leave the UI as-is */
      }
    }
    laterBtn.addEventListener("click", () =>
      setVisitLater(!laterCtl.classList.contains("is-later")));
    laterBadge.addEventListener("click", () => setVisitLater(false));
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

// "Get More Help with AI": stream one extra, more-concrete hint from the server's
// optional LLM endpoint (Server-Sent Events). Inert when the button is greyed out.
(function () {
  const root = document.querySelector(".solve");
  const wrap = document.getElementById("ai-help");
  if (!root || !wrap || wrap.dataset.enabled !== "1") return;

  const btn = document.getElementById("ai-help-btn");
  const label = btn.querySelector(".ai-help-label");
  const progress = document.getElementById("ai-help-progress");
  const bar = document.getElementById("ai-help-bar-fill");
  const statusEl = document.getElementById("ai-help-status");
  const output = document.getElementById("ai-help-output");
  const slug = root.dataset.slug;

  // Rough target length (chars) for a 3-5 sentence hint. The bar eases toward 92%
  // as text arrives, then snaps to 100% when the stream finishes — a real, if
  // approximate, sense of progress before we know the true length.
  const TARGET = 460;

  let busy = false, timer = null, t0 = 0;

  const showStatus = (t) => { statusEl.textContent = t; };
  const tick = () =>
    showStatus(`Writing your hint… ${((Date.now() - t0) / 1000).toFixed(1)}s`);

  function paint(kind, text) {
    // kind: "hint" (accent) or "error" (red). Rebuilds the box once, then updates
    // only the text node on subsequent streamed deltas.
    output.hidden = false;
    output.classList.toggle("is-error", kind === "error");
    let textEl = output.querySelector(".ai-help-text");
    if (!textEl) {
      const icon = kind === "error" ? "⚠️" : "✨";
      output.innerHTML =
        `<div class="ai-help-head"><span aria-hidden="true">${icon}</span> AI hint</div>` +
        `<div class="ai-help-text"></div>`;
      textEl = output.querySelector(".ai-help-text");
    }
    textEl.textContent = text;
  }

  async function getHelp() {
    if (busy) return;
    busy = true;
    btn.disabled = true;
    btn.classList.add("is-busy");
    progress.hidden = false;
    output.hidden = true;
    output.classList.remove("is-error");
    output.innerHTML = "";
    bar.style.width = "6%";
    showStatus("Contacting the AI…");
    t0 = Date.now();

    let text = "", errored = false;
    try {
      const resp = await fetch(`/api/problems/${slug}/help`, { method: "POST" });
      if (!resp.ok || !resp.body) {
        let detail = "Request failed";
        try { detail = (await resp.json()).detail || detail; } catch (_) { /* non-JSON */ }
        throw new Error(detail);
      }
      timer = setInterval(tick, 200);

      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let sep;
        while ((sep = buf.indexOf("\n\n")) !== -1) {
          const frame = buf.slice(0, sep);
          buf = buf.slice(sep + 2);
          const line = frame.split("\n").find((l) => l.startsWith("data:"));
          if (!line) continue;
          let evt;
          try { evt = JSON.parse(line.slice(5).trim()); } catch (_) { continue; }
          if (evt.type === "delta") {
            text += evt.text;
            paint("hint", text);
            bar.style.width = Math.min(92, 6 + (text.length / TARGET) * 86) + "%";
          } else if (evt.type === "error") {
            errored = true;
            paint("error", evt.message || "AI help failed.");
          }
        }
      }
    } catch (err) {
      errored = true;
      paint("error", err.message || "AI help failed.");
    } finally {
      if (timer) { clearInterval(timer); timer = null; }
      bar.style.width = "100%";
      busy = false;
      btn.disabled = false;
      btn.classList.remove("is-busy");
      if (errored) {
        progress.hidden = true;
        showStatus("");
      } else {
        showStatus("Done ✓");
        label.textContent = "Get another hint";
        setTimeout(() => { progress.hidden = true; }, 1600);
      }
    }
  }

  btn.addEventListener("click", getHelp);
})();
