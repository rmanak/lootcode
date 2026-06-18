// Problem list: filter as you type. The title search (and the difficulty/topic
// dropdowns) refresh the list in place instead of waiting for the "Filter"
// button — server-side so search still spans the whole bank, not just the page.
(function () {
  const form = document.querySelector(".search-form");
  const list = document.getElementById("problem-list");
  if (!form || !list) return;

  const search = form.querySelector('input[name="q"]');
  let timer = null;
  let seq = 0; // guards against an earlier fetch landing after a later one

  function buildUrl() {
    const params = new URLSearchParams();
    new FormData(form).forEach((v, k) => {
      if (String(v).trim() !== "") params.append(k, v);
    });
    const qs = params.toString();
    return qs ? "/?" + qs : "/";
  }

  function swap(doc, selector) {
    const next = doc.querySelector(selector);
    const cur = document.querySelector(selector);
    if (next && cur) cur.replaceWith(next);
  }

  async function refresh() {
    const url = buildUrl();
    const mine = ++seq;
    let html;
    try {
      const resp = await fetch(url, { headers: { "X-Requested-With": "fetch" } });
      if (!resp.ok) return;
      html = await resp.text();
    } catch (_) {
      return; // network hiccup — leave the page as it is
    }
    if (mine !== seq) return; // superseded by a newer keystroke
    const doc = new DOMParser().parseFromString(html, "text/html");
    // Swap the regions whose links embed the query string, so a later chip click
    // keeps the typed search. The form itself (and the focused input) is left be.
    swap(doc, "#problem-list");
    swap(doc, ".difficulty-filters");
    swap(doc, ".status-filters");
    const wasOpen = (document.getElementById("topic-expand") || {}).checked;
    swap(doc, ".topic-bar-wrap");
    const expand = document.getElementById("topic-expand");
    if (expand && wasOpen) expand.checked = true; // keep the bar expanded
    history.replaceState(null, "", url);
  }

  search.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(refresh, 200);
  });
})();
