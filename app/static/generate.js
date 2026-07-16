// Admin "Generate & verify": stream generation progress instead of a blank ~minute
// blocking POST. Progressive enhancement — if this script doesn't run, the form still
// posts normally to /admin/generate and the server renders the results. Mirrors the
// SSE shape of the "Get More Help with AI" endpoint.
(function () {
  const form = document.getElementById("gen-form");
  if (!form || !window.fetch) return;

  const submit = document.getElementById("gen-submit");
  const progress = document.getElementById("gen-progress");
  const bar = document.getElementById("gen-bar-fill");
  const statusEl = document.getElementById("gen-status");
  const liveError = document.getElementById("gen-live-error");
  const results = document.getElementById("gen-live-results");
  const heading = document.getElementById("gen-live-heading");
  const list = document.getElementById("gen-live-list");

  let busy = false, timer = null, t0 = 0, pct = 0, latest = "", count = 0;

  const setBar = (p) => { pct = p; bar.style.width = p + "%"; };
  function tick() {
    // Ease toward 92% (we have no true length signal), then snap to 100% on done.
    setBar(pct + (92 - pct) * 0.02);
    const secs = ((Date.now() - t0) / 1000).toFixed(1);
    statusEl.textContent = `${latest || "Working…"} (${secs}s)`;
  }

  function addTag(li, cls, text) {
    const s = document.createElement("span");
    s.className = cls;
    s.textContent = text;
    li.append(" ", s);
  }

  function addResult(evt) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = "/problems/" + encodeURIComponent(evt.slug);
    a.textContent = evt.title || evt.slug;
    li.appendChild(a);
    const v = evt.validation || {};
    if (v.solved) {
      addTag(li, "ok-tag", `verified ✓ (${v.passed}/${v.total})`);
    } else if (v.total !== undefined) {
      addTag(li, "warn-tag", `⚠ reference solution failed (${v.passed}/${v.total}) — review it`);
    }
    if (v.dropped && v.dropped.length) {
      addTag(li, "warn-tag", `dropped ${v.dropped.length} malformed test(s): ${v.dropped.join(", ")}`);
    }
    list.appendChild(li);
    count += 1;
    heading.textContent = `Created ${count} problem(s)`;
    results.hidden = false;
  }

  async function run() {
    // Reset UI for a fresh run.
    liveError.hidden = true;
    liveError.textContent = "";
    results.hidden = true;
    list.textContent = "";
    count = 0;
    busy = true;
    submit.disabled = true;
    submit.classList.add("is-busy");
    progress.hidden = false;
    latest = "Contacting the AI…";
    t0 = Date.now();
    setBar(6);

    let errored = false;
    try {
      const resp = await fetch("/admin/generate/stream", {
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
          } else if (evt.type === "result") {
            addResult(evt);
          } else if (evt.type === "error") {
            errored = true;
            liveError.textContent = evt.message || "Generation failed.";
            liveError.hidden = false;
          }
        }
      }
    } catch (err) {
      errored = true;
      liveError.textContent = err.message || "Generation failed.";
      liveError.hidden = false;
    } finally {
      if (timer) { clearInterval(timer); timer = null; }
      setBar(100);
      busy = false;
      submit.disabled = false;
      submit.classList.remove("is-busy");
      if (errored && count === 0) {
        progress.hidden = true;
        statusEl.textContent = "";
      } else {
        statusEl.textContent = count ? `Done ✓ — ${count} saved` : "Done ✓";
        setTimeout(() => { progress.hidden = true; }, 1800);
      }
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!busy) run();
  });
})();
