// Admin "Generate with AI" landing page, choice 1 (idea → statement).
// Streams progress from /admin/generate/statement/stream, then navigates to the
// statement review page. Without JS the form posts normally to
// /admin/generate/statement and the server issues the same redirect.
//
// The flow itself lives in sse.js — this page and the statement page were the
// same script twice, differing only in the URL and one word of status text.
(function () {
  window.lootcode.wireStreamedForm({
    form: document.getElementById("idea-form"),
    submit: document.getElementById("idea-submit"),
    progress: document.getElementById("idea-progress"),
    bar: document.getElementById("idea-bar-fill"),
    statusEl: document.getElementById("idea-status"),
    liveError: document.getElementById("gen-live-error"),
    url: "/admin/generate/statement/stream",
    doneText: "Done ✓ — opening statement…",
  });
})();
