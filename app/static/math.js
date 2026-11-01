// Typeset the math in rendered Markdown with the vendored KaTeX
// (static/vendor/katex/). The server has already done the hard part:
// pymdownx.arithmatex (app/templating.py) found every $…$ / $$…$$ before
// Markdown ran and wrapped it as
//   <span class="arithmatex">\(…\)</span>   inline
//   <div class="arithmatex">\[…\]</div>     display
// so this renders exactly those elements and nothing else — a bare "$5" in
// prose is never mistaken for math. If KaTeX failed to load, or a formula does
// not parse, the TeX source stays on the page, readable. See
// docs/math-in-statements.md.
(function () {
  "use strict";

  function typeset(root) {
    if (typeof window.katex === "undefined") return;
    var els = (root || document).querySelectorAll(".arithmatex:not([data-typeset])");
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      var tex = el.textContent.trim();
      var open = tex.slice(0, 2), close = tex.slice(-2);
      var display;
      if (open === "\\(" && close === "\\)") display = false;
      else if (open === "\\[" && close === "\\]") display = true;
      else continue;
      try {
        // throwOnError:false shows a bad formula as red source with the parse
        // error as its tooltip, instead of blanking it. `trust` stays at its
        // default (false), so \href, \includegraphics & co. are refused.
        window.katex.render(tex.slice(2, -2), el, {
          displayMode: display,
          throwOnError: false,
        });
        el.setAttribute("data-typeset", "");
      } catch (e) {
        /* leave the TeX source in place */
      }
    }
  }

  // Exposed for any page that inserts rendered Markdown after load.
  window.lootcodeTypeset = typeset;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { typeset(); });
  } else {
    typeset();
  }
})();
