// Admin "Generate with AI" landing page, choice 1 (idea → statement).
// Progressive enhancement: streams generation progress from
// /admin/generate/statement/stream, then navigates to the statement review page.
// Without JS the form posts normally to /admin/generate/statement and the server
// issues the same redirect. Mirrors the SSE shape of the "Get More Help with AI"
// endpoint.
(function () {
  const form = document.getElementById("idea-form");
  if (!form || !window.fetch) return;

  const submit = document.getElementById("idea-submit");
  const progress = document.getElementById("idea-progress");
  const bar = document.getElementById("idea-bar-fill");
  const statusEl = document.getElementById("idea-status");
  const liveError = document.getElementById("gen-live-error");

  let busy = false, timer = null, t0 = 0, pct = 0, latest = "";

  const setBar = (p) => { pct = p; bar.style.width = p + "%"; };
  function tick() {
    setBar(pct + (92 - pct) * 0.03);
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
      const resp = await fetch("/admin/generate/statement/stream", {
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
        statusEl.textContent = "Done ✓ — opening statement…";
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
