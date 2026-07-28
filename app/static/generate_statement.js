// Admin statement-review page. Two behaviors, both progressive enhancements:
//   1. Re-run the duplicate check against the (possibly edited) statement, updating
//      the inferred title/slug and the similar-problem list in place.
//   2. Generate the full problem from the statement, streaming progress from
//      /admin/generate/full/stream, then navigating to its review page.
// Without JS the form posts normally to /admin/generate/full and the server issues
// the same redirect; the duplicate check then just reflects the server-rendered state.
(function () {
  const sid = (document.querySelector('input[name="sid"]') || {}).value || "";
  const statementEl = document.getElementById("statement");

  // --- 1. duplicate re-check ------------------------------------------------
  const recheck = document.getElementById("dup-recheck");
  const dupTitle = document.getElementById("dup-title");
  const dupSlug = document.getElementById("dup-slug");
  const dupList = document.getElementById("dup-list");
  const fullTitle = document.getElementById("full-title");
  const fullSlug = document.getElementById("full-slug");

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function renderSimilar(list) {
    if (!list || !list.length) {
      dupList.innerHTML = '<p class="muted">No obviously-similar problems found — looks new.</p>';
      return;
    }
    const items = list.map((s) => {
      const tags = (s.shared_tags && s.shared_tags.length)
        ? ` <span class="muted">· shared tags: ${esc(s.shared_tags.join(", "))}</span>` : "";
      return `<li><a href="/problems/${encodeURIComponent(s.slug)}" target="_blank" rel="noopener">${esc(s.title)}</a> `
        + `<code>${esc(s.slug)}</code> <span class="muted">· ${esc(s.difficulty)}</span>${tags}</li>`;
    }).join("");
    dupList.innerHTML = `<p class="muted">${list.length} existing problem(s) look similar — make sure this isn't a duplicate:</p><ul>${items}</ul>`;
  }

  async function runRecheck() {
    if (!recheck || !window.fetch || !statementEl) return;
    recheck.disabled = true;
    const original = recheck.textContent;
    recheck.textContent = "Checking…";
    try {
      const body = new FormData();
      body.append("sid", sid);
      body.append("statement", statementEl.value);
      const resp = await fetch("/admin/generate/duplicate-check", { method: "POST", body });
      if (!resp.ok) throw new Error("check failed");
      const data = await resp.json();
      if (dupTitle) dupTitle.textContent = data.title || "—";
      if (dupSlug) dupSlug.textContent = data.slug || "—";
      if (fullTitle) fullTitle.value = data.title || "";
      if (fullSlug) fullSlug.value = data.slug || "";
      renderSimilar(data.similar);
    } catch (_) {
      /* leave the last-good check in place */
    } finally {
      recheck.disabled = false;
      recheck.textContent = original;
    }
  }
  if (recheck) recheck.addEventListener("click", runRecheck);

  // If the statement is edited, the cached title/slug no longer describe it — clear
  // the hidden fields so the full-generation step re-derives them from the new text.
  if (statementEl) {
    let seeded = statementEl.value;
    statementEl.addEventListener("input", () => {
      if (statementEl.value !== seeded) {
        seeded = statementEl.value;
        if (fullTitle) fullTitle.value = "";
        if (fullSlug) fullSlug.value = "";
      }
    });
  }

  // --- 2. full-problem generation (streamed) --------------------------------
  // The flow lives in sse.js; this page differs from the idea page only in the
  // URL, one word of status text, and a gentler bar (filling in a whole problem
  // takes longer than writing a statement).
  window.lootcode.wireStreamedForm({
    form: document.getElementById("full-form"),
    submit: document.getElementById("full-submit"),
    progress: document.getElementById("full-progress"),
    bar: document.getElementById("full-bar-fill"),
    statusEl: document.getElementById("full-status"),
    liveError: document.getElementById("gen-live-error"),
    url: "/admin/generate/full/stream",
    doneText: "Done \u2713 \u2014 opening review\u2026",
    ease: 0.02,
  });
})();
