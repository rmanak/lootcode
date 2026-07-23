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
  const form = document.getElementById("full-form");
  if (!form || !window.fetch) return;

  const submit = document.getElementById("full-submit");
  const progress = document.getElementById("full-progress");
  const bar = document.getElementById("full-bar-fill");
  const statusEl = document.getElementById("full-status");
  const liveError = document.getElementById("gen-live-error");

  let busy = false, timer = null, t0 = 0, pct = 0, latest = "";
  const setBar = (p) => { pct = p; bar.style.width = p + "%"; };
  function tick() {
    setBar(pct + (92 - pct) * 0.02);
    const secs = ((Date.now() - t0) / 1000).toFixed(1);
    statusEl.textContent = `${latest || "Working…"} (${secs}s)`;
  }

  async function run() {
    if (liveError) { liveError.hidden = true; liveError.textContent = ""; }
    busy = true;
    submit.disabled = true;
    submit.classList.add("is-busy");
    progress.hidden = false;
    latest = "Contacting the AI…";
    t0 = Date.now();
    setBar(6);

    let errored = false, redirect = null;
    try {
      const resp = await fetch("/admin/generate/full/stream", {
        method: "POST", body: new FormData(form),
      });
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
          if (evt.type === "status") {
            latest = evt.message || latest;
          } else if (evt.type === "done") {
            redirect = evt.redirect || null;
          } else if (evt.type === "error") {
            errored = true;
            if (liveError) {
              liveError.textContent = evt.message || "Generation failed.";
              liveError.hidden = false;
            }
          }
        }
      }
    } catch (err) {
      errored = true;
      if (liveError) {
        liveError.textContent = err.message || "Generation failed.";
        liveError.hidden = false;
      }
    } finally {
      if (timer) { clearInterval(timer); timer = null; }
      setBar(100);
      if (redirect && !errored) {
        statusEl.textContent = "Done ✓ — opening review…";
        window.location.assign(redirect);
        return;
      }
      busy = false;
      submit.disabled = false;
      submit.classList.remove("is-busy");
      progress.hidden = true;
      statusEl.textContent = "";
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!busy) run();
  });
})();
