// Shared Server-Sent-Events plumbing for the three streamed features:
// "Get More Help with AI" (app.js), idea → statement (generate.js) and
// statement → problem (generate_statement.js).
//
// The frame reader below was byte-identical in all three files, and so were the
// error preamble and the creeping progress bar. The two admin generation pages
// were the same script twice over, differing only in a URL and one word of
// status text — so they now share `wireStreamedForm` outright.
//
// Every consumer is a progressive enhancement: without JS the same form posts
// normally and the server issues the same redirect.
window.lootcode = window.lootcode || {};
(function (ns) {
  "use strict";

  // POST `url` and hand each decoded SSE frame to `onEvent`.
  //
  // Server frames are `data: {json}\n\n` (see admin_generate._sse_stream). A
  // frame that isn't JSON is skipped rather than aborting the stream: losing one
  // status update is better than losing the run. A non-OK response carries its
  // reason in a JSON `detail`, which is what the user should see.
  // `onOpen` fires once the response is accepted and before the first frame, so
  // a caller can start its timer only after the request is known to be live.
  async function postStream(url, { body = null, onEvent, onOpen = null }) {
    const resp = await fetch(url, body === null
      ? { method: "POST" }
      : { method: "POST", body });
    if (!resp.ok || !resp.body) {
      let detail = "Request failed";
      try { detail = (await resp.json()).detail || detail; } catch (_) { /* non-JSON */ }
      throw new Error(detail);
    }
    if (onOpen) onOpen();
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
        onEvent(evt);
      }
    }
  }

  // A progress bar that eases toward 92% while we wait, then snaps to 100%.
  // We can't know how long the model will take, so this is honest-but-vague: it
  // never reaches the end on its own, and the elapsed seconds are real.
  //
  // `ease` is how fast it creeps — statement → full problem is the slower job and
  // uses a gentler value, so the bar doesn't sit pinned at 92% for a minute.
  function progressBar({ bar, statusEl, ease = 0.03 }) {
    let timer = null, t0 = 0, pct = 0, latest = "";
    const set = (p) => { pct = p; if (bar) bar.style.width = p + "%"; };
    function tick() {
      set(pct + (92 - pct) * ease);
      const secs = ((Date.now() - t0) / 1000).toFixed(1);
      if (statusEl) statusEl.textContent = `${latest || "Working…"} (${secs}s)`;
    }
    return {
      set,
      note: (msg) => { if (msg) latest = msg; },
      start(msg) { latest = msg || ""; t0 = Date.now(); set(6); },
      run() { if (!timer) timer = setInterval(tick, 200); },
      stop() { if (timer) { clearInterval(timer); timer = null; } set(100); },
      elapsed: () => Date.now() - t0,
    };
  }

  // The whole "submit a form, stream progress, navigate where the server says"
  // flow shared by both admin generation pages.
  //
  // Options: form, submit, progress, bar, statusEl, liveError (elements); url;
  // doneText (shown while navigating); errorText (fallback message); ease.
  function wireStreamedForm(opts) {
    const { form, submit, progress, bar, statusEl, liveError, url } = opts;
    if (!form || !window.fetch) return;
    const errorText = opts.errorText || "Generation failed.";
    const meter = progressBar({ bar, statusEl, ease: opts.ease });
    let busy = false;

    const fail = (msg) => {
      if (!liveError) return;
      liveError.textContent = msg || errorText;
      liveError.hidden = false;
    };

    async function run() {
      if (liveError) { liveError.hidden = true; liveError.textContent = ""; }
      busy = true;
      submit.disabled = true;
      submit.classList.add("is-busy");
      progress.hidden = false;
      meter.start("Contacting the AI…");

      let errored = false, redirect = null;
      try {
        await ns.postStream(url, {
          body: new FormData(form),
          // Only once the request is accepted: a rejected one shows its error
          // rather than a bar counting up behind it.
          onOpen: () => meter.run(),
          onEvent(evt) {
            if (evt.type === "status") {
              meter.note(evt.message);
            } else if (evt.type === "done") {
              redirect = evt.redirect || null;
            } else if (evt.type === "error") {
              errored = true;
              fail(evt.message);
            }
          },
        });
      } catch (err) {
        errored = true;
        fail(err.message);
      } finally {
        meter.stop();
        if (redirect && !errored) {
          if (statusEl) statusEl.textContent = opts.doneText || "Done ✓";
          window.location.assign(redirect);
          return;
        }
        busy = false;
        submit.disabled = false;
        submit.classList.remove("is-busy");
        progress.hidden = true;
        if (statusEl) statusEl.textContent = "";
      }
    }

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!busy) run();
    });
  }

  ns.postStream = postStream;
  ns.progressBar = progressBar;
  ns.wireStreamedForm = wireStreamedForm;
})(window.lootcode);
