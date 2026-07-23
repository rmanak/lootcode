// Admin edit page AND AI review page: run the canonical solution against the
// current (unsaved) tests. Works on either form — the edit form carries a
// data-slug and posts to the per-problem verify URL; the review/new form has no
// slug and posts to the slug-less /admin/verify. Both return identical detail.
(function () {
  const btn = document.getElementById("verify-btn");
  if (!btn) return;
  const form = btn.closest("form");
  if (!form) return;

  const slug = form.dataset.slug || "";
  const endpoint = slug ? `/admin/problems/${slug}/verify` : "/admin/verify";
  const statusEl = document.getElementById("verify-status");
  const out = document.getElementById("verify-results");
  const val = (name) => {
    const el = form.querySelector(`[name="${name}"]`);
    return el ? el.value : "";
  };

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    statusEl.textContent = "Running…";
    out.innerHTML = "";
    try {
      const resp = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: val("canonical_solution"),
          kind: val("kind"),
          function_name: val("function_name"),
          params: val("params"),
          return_type: val("return_type"),
          class_name: val("class_name"),
          class_methods_json: val("class_methods_json"),
          tests_json: val("tests_json"),
          compare: val("compare"),
        }),
      });
      if (!resp.ok) {
        const e = await resp.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(e.detail || "Request failed");
      }
      render(await resp.json());
    } catch (err) {
      out.innerHTML = `<div class="run-error">${esc(err.message)}</div>`;
    } finally {
      btn.disabled = false;
      statusEl.textContent = "";
    }
  });

  function render(d) {
    const head = `<div class="summary ${d.solved ? "ok" : "no"}">
      <strong>${d.solved ? "Canonical passes all tests 🎉" : `Passed ${d.passed_count} / ${d.total_count}`}</strong>
      <span>Score ${d.score}/100</span><span>${d.runtime_ms} ms</span></div>`;

    const cases = d.results.map((r) => {
      const cls = r.passed ? "pass" : r.status === "timeout" ? "timeout" : "fail";
      const hid = r.hidden ? ' <span class="hid">hidden</span>' : "";
      let detail = "";
      if (!r.passed) {
        detail = `<pre class="kv">expected: ${esc(JSON.stringify(r.expected))}\n` +
                 `actual:   ${esc(JSON.stringify(r.actual))}` +
                 `${r.error ? "\nerror:    " + esc(r.error) : ""}</pre>`;
      }
      return `<div class="case ${cls}">
        <span class="dot"></span>
        <span class="label">${esc(r.name)}${hid}</span>
        <span class="st">${r.passed ? "passed" : esc(r.status)}</span>
        <span class="t">${r.time_ms} ms</span>${detail}</div>`;
    }).join("");

    out.innerHTML = head + `<div class="cases">${cases}</div>`;
  }

  function esc(s) {
    return (s == null ? "" : String(s)).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
})();
