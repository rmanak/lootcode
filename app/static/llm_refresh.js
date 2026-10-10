// "Re-check" button for the optional LLM endpoint.
//
// The server re-probes LLM_HELP_URL in the background every
// LLM_HELP_PROBE_INTERVAL seconds; this is the immediate, manual version (and the
// only one when that interval is 0). Any element carrying data-llm-refresh re-runs
// the probe; if the endpoint is now reachable we reload, so the server re-renders
// the page with the AI features enabled.
(function () {
  const buttons = document.querySelectorAll("[data-llm-refresh]");
  if (!buttons.length) return;

  buttons.forEach((btn) => {
    // Optional sibling for feedback; without one the button's own label is used.
    const statusEl = document.getElementById(btn.dataset.llmRefreshStatus || "");
    const idle = btn.textContent;
    const say = (msg) => {
      if (statusEl) statusEl.textContent = msg;
      else btn.textContent = msg;
    };

    btn.addEventListener("click", async () => {
      btn.disabled = true;
      say("Checking…");
      try {
        const resp = await fetch("/api/llm/refresh", { method: "POST" });
        if (!resp.ok) throw new Error(`Probe failed (${resp.status})`);
        const d = await resp.json();
        if (d.available) {
          say("Connected — reloading…");
          window.location.reload();
          return; // leave the button disabled while the page swaps out
        }
        say(`No LLM at ${d.endpoint || "the configured endpoint"}`);
      } catch (err) {
        say(err.message || "Check failed");
      }
      btn.disabled = false;
      if (!statusEl) window.setTimeout(() => { btn.textContent = idle; }, 4000);
    });
  });
})();
