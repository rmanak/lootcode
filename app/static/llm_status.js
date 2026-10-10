// Live availability of the optional LLM endpoint.
//
// The server re-probes LLM_HELP_URL in the background (help_generator.
// watch_availability); this polls the cached result, GET /api/llm/status, which
// makes no outbound request, and fires a `lootcode:llm-status` event on document
// ({detail: {available}}) whenever it changes. The AI buttons listen for it, so
// they turn on when the LLM server comes up and grey out when it goes away, with
// no reload. The initial state comes from the tag: <script data-available="1|0">.
//
// Polls only while the tab is visible, and once immediately on becoming visible.
(function () {
  const script = document.currentScript;
  let available = !!script && script.dataset.available === "1";
  const POLL_MS = 5000;
  let timer = null;

  async function poll() {
    timer = null;
    try {
      const resp = await fetch("/api/llm/status", { cache: "no-store" });
      if (resp.ok) {
        const now = !!(await resp.json()).available;
        if (now !== available) {
          available = now;
          document.dispatchEvent(new CustomEvent("lootcode:llm-status",
            { detail: { available } }));
        }
      }
    } catch (_) {
      // lootcode itself is unreachable: keep the last known state.
    }
    schedule();
  }

  function schedule() {
    if (timer === null && document.visibilityState === "visible") {
      timer = window.setTimeout(poll, POLL_MS);
    }
  }

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState !== "visible") {
      if (timer !== null) { window.clearTimeout(timer); timer = null; }
    } else if (timer === null) {
      poll();
    }
  });
  schedule();
})();
