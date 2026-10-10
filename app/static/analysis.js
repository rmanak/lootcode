// "✨ Analysis": an AI report on the editor's code, in the shape of LeetCode's
// Analysis panel — a header card (pillar checklist, summary, Approach) followed
// by an Efficiency card (Time / Space tabs) and a Code Style card. Rendered into
// #analysis, between the Run & Score row and the test results.
//
// The server grades the code, then streams the model's schema-constrained JSON
// as SSE (see POST /api/problems/{slug}/analyze): `status`, `verdict`,
// `progress` (chars + completed pillars), then `result` or `error`.
(function () {
  "use strict";
  const root = document.querySelector(".solve");
  const btn = document.getElementById("analysis-btn");
  const panel = document.getElementById("analysis");
  if (!root || !btn || !panel || btn.dataset.enabled !== "1") return;

  const slug = root.dataset.slug;
  const label = btn.querySelector(".analysis-label");
  const PILLARS = [["approach", "Approach"], ["efficiency", "Efficiency"],
                   ["code_style", "Code Style"]];
  // Roughly how long a full report is, so the bar tracks real progress.
  const TARGET_CHARS = 1350;

  const ICONS = {
    approach: '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
    efficiency: '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
    code_style: '<path d="M13 7 8.7 2.7a2.41 2.41 0 0 0-3.4 0L2.7 5.3a2.41 2.41 0 0 0 0 3.4L7 13"/><path d="m8 6 2-2"/><path d="m18 16 2-2"/><path d="m17 11 4.3 4.3c.94.94.94 2.46 0 3.4l-2.6 2.6c-.94.94-2.46.94-3.4 0L11 17"/><path d="M21.17 6.81a1 1 0 0 0-3.99-3.99L3.84 16.17a2 2 0 0 0-.5.83l-1.32 4.35a.5.5 0 0 0 .62.62l4.35-1.32a2 2 0 0 0 .83-.5z"/><path d="m15 5 4 4"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
  };
  const icon = (name, cls) =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" ` +
    `stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg>`;

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  // Prose with `identifiers` in backticks → inline <code>.
  const rich = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");

  // "O(n log n)", "O(n^2)", "O(n + m)" → math-styled HTML: single-letter
  // variables in italics, exponents as superscripts, function names upright.
  function bigO(raw) {
    let html = "";
    const re = /\^(?:\{([^}]*)\}|\(([^)]*)\)|([\w.]+))|([A-Za-z]{2,})|([A-Za-z])|([^A-Za-z^]+)|\^/g;
    for (const m of String(raw || "").matchAll(re)) {
      const sup = m[1] ?? m[2] ?? m[3];
      if (sup !== undefined) html += `<sup>${bigO(sup)}</sup>`;
      else if (m[4]) html += `<span class="an-fn">${esc(m[4])}</span>`;
      else if (m[5]) html += `<i>${esc(m[5])}</i>`;
      else html += esc(m[0]);
    }
    return `<span class="an-math">${html}</span>`;
  }

  const labels = (list) => (list || []).map(esc).join('<span class="an-slash">/</span>');
  const row = (k, v, cls) =>
    `<dt>${k}:</dt><dd${cls ? ` class="${cls}"` : ""}>${v}</dd>`;
  const heading = (key, text) =>
    `<h3 class="an-title">${icon(key, "an-icon")}<span>${text}</span></h3>`;

  function shell() {
    const pills = PILLARS.map(([k, l]) =>
      `<span class="an-pillar" data-pillar="${k}">` +
      `<span class="an-tick">${icon("check", "an-check")}<span class="an-spin"></span></span>${l}</span>`).join("");
    panel.innerHTML =
      `<section class="an-card an-main">
        <div class="an-head">
          <div class="an-pillars">${pills}</div>
          <span class="an-verdict" hidden></span>
          <button type="button" class="an-close" title="Close analysis" aria-label="Close analysis">×</button>
        </div>
        <div class="an-body">
          <div class="an-progress">
            <div class="an-bar"><span></span></div>
            <span class="an-status">Starting…</span>
          </div>
        </div>
      </section>`;
    panel.hidden = false;
    panel.querySelector(".an-close").addEventListener("click", () => {
      panel.hidden = true;
      panel.innerHTML = "";
    });
  }

  const $ = (sel) => panel.querySelector(sel);
  const setStatus = (t) => { const el = $(".an-status"); if (el) el.textContent = t; };
  const setBar = (pct) => { const el = $(".an-bar > span"); if (el) el.style.width = pct + "%"; };

  function tickPillars(n) {
    PILLARS.forEach(([k], i) => {
      const el = panel.querySelector(`[data-pillar="${k}"]`);
      if (el) el.classList.toggle("is-done", i < n);
    });
  }

  function showVerdict(v) {
    const el = $(".an-verdict");
    if (!el) return;
    const ok = v.status === "Accepted";
    el.className = "an-verdict " + (ok ? "ok" : "no");
    el.textContent = v.total ? `${v.status} · ${v.passed}/${v.total} tests` : v.status;
    el.hidden = false;
  }

  function showError(msg) {
    const body = $(".an-body");
    if (body) body.innerHTML = `<p class="an-error">⚠️ ${esc(msg || "AI analysis failed.")}</p>`;
    panel.querySelectorAll(".an-pillar").forEach((p) => p.classList.add("is-idle"));
  }

  function render(a) {
    const body = $(".an-body");
    if (!body) return;  // closed while the report was still streaming
    tickPillars(PILLARS.length);
    const ap = a.approach, eff = a.efficiency, cs = a.code_style;
    body.innerHTML =
      (a.summary ? `<p class="an-summary">${rich(a.summary)}</p><hr class="an-rule">` : "") +
      heading("approach", "Approach") +
      `<dl class="an-rows">
        ${row("Current", labels(ap.current))}
        ${row("Suggested", labels(ap.suggested), "an-good")}
        ${ap.key_idea ? row("Key Idea", rich(ap.key_idea)) : ""}
        ${ap.consider ? row("Consider", rich(ap.consider)) : ""}
      </dl>`;

    const effCard = document.createElement("section");
    effCard.className = "an-card";
    effCard.innerHTML =
      heading("efficiency", "Efficiency") +
      `<div class="an-tabs" role="tablist">
        <button type="button" role="tab" class="an-tab is-active" data-tab="time" aria-selected="true">Time Complexity</button>
        <button type="button" role="tab" class="an-tab" data-tab="space" aria-selected="false">Space Complexity</button>
      </div>` +
      ["time", "space"].map((k, i) =>
        `<dl class="an-rows" data-tab-view="${k}"${i ? " hidden" : ""}>
          ${row("Current complexity", bigO(eff[k].current))}
          ${row("Suggested complexity", bigO(eff[k].suggested), "an-good")}
          ${eff[k].suggestions ? row("Suggestions", rich(eff[k].suggestions)) : ""}
        </dl>`).join("");
    effCard.querySelectorAll(".an-tab").forEach((tab) => tab.addEventListener("click", () => {
      effCard.querySelectorAll(".an-tab").forEach((t) => {
        const on = t === tab;
        t.classList.toggle("is-active", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
      });
      effCard.querySelectorAll("[data-tab-view]").forEach((v) => {
        v.hidden = v.dataset.tabView !== tab.dataset.tab;
      });
    }));

    const styleCard = document.createElement("section");
    styleCard.className = "an-card";
    styleCard.innerHTML =
      heading("code_style", "Code Style") +
      `<dl class="an-rows an-rows-loose">
        ${row("Readability", esc(cs.readability))}
        ${row("Structure", esc(cs.structure))}
        ${cs.suggestions ? row("Suggestions", rich(cs.suggestions)) : ""}
      </dl>`;

    panel.append(effCard, styleCard);
  }

  let busy = false;

  async function analyze() {
    if (busy) return;
    const editor = window.lootcode && window.lootcode.editor;
    const code = editor ? editor.getValue() : "";
    busy = true;
    btn.disabled = true;
    btn.classList.add("is-busy");
    label.textContent = "Analyzing…";
    shell();
    setBar(4);

    let timer = null;
    const t0 = Date.now();
    let note = "Starting…";
    const tick = () => setStatus(`${note} ${((Date.now() - t0) / 1000).toFixed(1)}s`);
    let got = false;
    try {
      await window.lootcode.postStream(`/api/problems/${slug}/analyze`, {
        body: JSON.stringify({ code }),
        headers: { "Content-Type": "application/json" },
        onOpen: () => { timer = setInterval(tick, 200); },
        onEvent(evt) {
          if (evt.type === "status") {
            note = evt.message || note;
            tick();
          } else if (evt.type === "verdict") {
            showVerdict(evt);
            setBar(12);
          } else if (evt.type === "progress") {
            setBar(Math.min(94, 12 + (evt.chars / TARGET_CHARS) * 82));
            tickPillars(evt.pillars || 0);
          } else if (evt.type === "result") {
            got = true;
            render(evt.analysis);
          } else if (evt.type === "error") {
            got = true;
            showError(evt.message);
          }
        },
      });
      if (!got) showError("The analysis ended without a result.");
    } catch (err) {
      showError(err.message);
    } finally {
      if (timer) clearInterval(timer);
      busy = false;
      btn.disabled = false;
      btn.classList.remove("is-busy");
      label.textContent = "Analysis";
    }
  }

  btn.addEventListener("click", analyze);
})();
