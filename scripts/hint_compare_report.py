#!/usr/bin/env python3
"""Render a fix dry-run/apply report into a browsable old -> new compare page.

`improve_hints.py fix` (dry-run or --apply) now writes .hints/fix-dry.json /
.hints/fix-apply.json: the proposed replacement hints for each flagged problem,
plus the judge's verdicts on the *new* set. This turns that into a single static
HTML page showing BEFORE (current hints) beside AFTER (the regenerated set), each
tier badged ok / reveals / vague, so you can eyeball what a fix would change before
committing to --apply. Old-side labels are pulled from .hints/audit.json when
present; the file is otherwise self-contained (no server, no external assets).

    python scripts/improve_hints.py fix --from-report --slug coin-change --dry-run
    python scripts/hint_compare_report.py --open       # fix-dry.json -> compare.html

    python scripts/hint_compare_report.py --apply       # read fix-apply.json instead
"""
from __future__ import annotations

import argparse
import json
import pathlib
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent.parent
HINTS = ROOT / ".hints"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hint fixes — __COUNT__ problems</title>
<style>
:root{
  --bg:#0f1216; --panel:#171b21; --panel2:#1e232b; --line:#2a313b;
  --fg:#e6e9ee; --dim:#9aa4b2; --faint:#6b7482;
  --reveals:#f0616d; --vague:#e2b13c; --ok:#4fbf87; --accent:#5aa0f0;
  --wrote:#4fbf87; --would:#5aa0f0; --keep:#6b7482;
}
@media (prefers-color-scheme: light){
  :root{
    --bg:#f6f7f9; --panel:#fff; --panel2:#f0f2f5; --line:#dde1e7;
    --fg:#1a1f26; --dim:#5b6472; --faint:#8b94a2;
    --reveals:#d63241; --vague:#b7860b; --ok:#1f9d5f; --accent:#2f6fd6;
    --wrote:#1f9d5f; --would:#2f6fd6; --keep:#8b94a2;
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--panel);
  border-bottom:1px solid var(--line);padding:12px 20px}
h1{margin:0 0 2px;font-size:17px}
.meta{color:var(--dim);font-size:12px;margin-bottom:10px}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chip{border:1px solid var(--line);background:var(--panel2);color:var(--fg);
  padding:5px 11px;border-radius:999px;cursor:pointer;font-size:12.5px;user-select:none}
.chip:hover{border-color:var(--faint)}
.chip.on{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 18%,var(--panel2));font-weight:600}
.chip .n{opacity:.7;margin-left:4px}
input[type=search]{flex:1;min-width:180px;background:var(--panel2);border:1px solid var(--line);
  color:var(--fg);padding:6px 10px;border-radius:7px;font-size:13px}
label.toggle{display:flex;gap:5px;align-items:center;color:var(--dim);font-size:12.5px;cursor:pointer}
main{max-width:1080px;margin:0 auto;padding:16px 20px 80px}
.count{color:var(--dim);font-size:12.5px;margin:4px 0 12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:9px;
  padding:12px 14px;margin-bottom:12px}
.card h2{margin:0 0 10px;font-size:15px;display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.slug{font-family:ui-monospace,monospace}
.badge{font-size:10.5px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;
  padding:2px 7px;border-radius:5px;border:1px solid transparent}
.badge.wrote{color:#fff;background:var(--wrote)}
.badge.would{color:#fff;background:var(--would)}
.badge.keep{color:var(--keep);border-color:var(--keep)}
.badge.clean{color:var(--ok);border-color:var(--ok)}
.badge.residual{color:var(--reveals);border-color:var(--reveals)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:720px){.cols{grid-template-columns:1fr}}
.col h3{margin:0 0 6px;font-size:11px;text-transform:uppercase;letter-spacing:.6px;color:var(--faint)}
.col.before h3{color:var(--reveals)}
.col.after h3{color:var(--ok)}
.hints{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px}
.hint{padding:7px 9px;border-radius:7px;background:var(--panel2);border:1px solid transparent}
.hint.reveals{border-color:color-mix(in srgb,var(--reveals) 45%,var(--line))}
.hint.vague{border-color:color-mix(in srgb,var(--vague) 45%,var(--line))}
.htop{display:flex;gap:7px;align-items:baseline}
.tier{font-weight:700;color:var(--faint);font-size:11.5px}
.htext{font-size:13px;flex:1}
.labels{display:flex;gap:5px;flex-wrap:wrap;margin-top:3px;padding-left:24px}
.lab{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px;
  padding:1px 6px;border-radius:4px}
.lab.reveals{color:#fff;background:var(--reveals)}
.lab.vague{color:#241c00;background:var(--vague)}
.lab.ok{color:var(--ok);border:1px solid var(--ok)}
.lab.regex{color:var(--dim);border:1px solid var(--line)}
.reason{color:var(--dim);font-size:12px;margin:2px 0 0 24px;font-style:italic}
.empty{color:var(--faint);text-align:center;padding:40px}
footer{color:var(--faint);font-size:11.5px;text-align:center;padding:20px}
</style>
</head>
<body>
<header>
  <h1>Hint fixes — before → after</h1>
  <div class="meta">__META__</div>
  <div class="controls">
    <span class="chip status" data-status="changed">changed<span class="n">__N_CHANGED__</span></span>
    <span class="chip status" data-status="keep">kept<span class="n">__N_KEEP__</span></span>
    <input type="search" id="q" placeholder="filter by slug…" autocomplete="off">
    <label class="toggle"><input type="checkbox" id="residual"> new set still flagged</label>
  </div>
</header>
<main>
  <div class="count" id="count"></div>
  <div id="list"></div>
  <div class="empty" id="empty" hidden>No problems match.</div>
</main>
<footer>Generated from __SRC__ · dry-run preview writes nothing to meta.json</footer>
<script>
const DATA = __DATA__;
const list = document.getElementById('list');
const countEl = document.getElementById('count');
const emptyEl = document.getElementById('empty');
const q = document.getElementById('q');
const active = new Set(['changed']);   // hide the "keep" (unchanged) ones by default

document.querySelectorAll('.chip.status').forEach(ch=>{
  const s = ch.dataset.status;
  if(active.has(s)) ch.classList.add('on');
  ch.onclick = ()=>{ ch.classList.toggle('on');
    ch.classList.contains('on')?active.add(s):active.delete(s); render(); };
});
q.oninput = render;
document.getElementById('residual').onchange = render;

function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
const changed = r => r.outcome==='wrote' || r.outcome==='would';

function hintList(hints, verd, heur){
  verd = verd||{}; heur = heur||{};
  return (hints||[]).map((h,i)=>{
    const t=i+1, v=verd[t]||{}, lab=v.label||'';
    const cls = lab==='reveals'?'reveals':(lab==='vague'?'vague':'');
    const labs=[];
    if(lab==='reveals') labs.push('<span class="lab reveals">reveals</span>');
    else if(lab==='vague') labs.push('<span class="lab vague">vague</span>');
    else if(lab==='ok') labs.push('<span class="lab ok">ok</span>');
    if(heur[t]) labs.push('<span class="lab regex" title="'+esc(heur[t])+'">regex</span>');
    const reason=(lab==='reveals'||lab==='vague')&&v.reason?'<div class="reason">'+esc(v.reason)+'</div>':'';
    return `<li class="hint ${cls}"><div class="htop"><span class="tier">H${t}</span>
      <span class="htext">${esc(h)}</span></div>
      ${labs.length?`<div class="labels">${labs.join('')}</div>`:''}${reason}</li>`;
  }).join('') || '<li class="hint"><span class="htext" style="color:var(--faint)">(none)</span></li>';
}

function card(r){
  const oBadge = changed(r)
    ? `<span class="badge ${r.outcome}">${r.outcome==='wrote'?'wrote':'would write'}</span>`
    : `<span class="badge keep">kept (not better)</span>`;
  const clean = r.accepted
    ? '<span class="badge clean">new set clean</span>'
    : (r.new_flagged&&r.new_flagged.length?`<span class="badge residual">still flags ${r.new_flagged.join(', ')}</span>`:'');
  const delta = (r.old_ct!=null?r.old_ct:'?')+' → '+(r.new_ct!=null?r.new_ct:'?')+' flags';
  return `<div class="card">
    <h2><span class="slug">${esc(r.slug)}</span>${oBadge}${clean}
      <span style="color:var(--faint);font-size:12px">${delta}</span></h2>
    <div class="cols">
      <div class="col before"><h3>Before (current)</h3>
        <ul class="hints">${hintList(r.old, r.old_verdicts, r.old_heuristic)}</ul></div>
      <div class="col after"><h3>After (proposed)</h3>
        <ul class="hints">${hintList(r.new, r.new_verdicts, r.new_heuristic)}</ul></div>
    </div></div>`;
}

function render(){
  const needle=q.value.trim().toLowerCase();
  const resid=document.getElementById('residual').checked;
  let rows=DATA.filter(r=>{
    const bucket = changed(r) ? 'changed' : 'keep';
    return active.has(bucket);
  });
  if(needle) rows=rows.filter(r=>r.slug.toLowerCase().includes(needle));
  if(resid) rows=rows.filter(r=>!r.accepted && (r.new_flagged||[]).length);
  rows.sort((a,b)=> (changed(b)-changed(a)) || (a.accepted-b.accepted) || a.slug.localeCompare(b.slug));
  countEl.textContent=`${rows.length} shown`;
  emptyEl.hidden=rows.length>0;
  list.innerHTML=rows.map(card).join('');
}
render();
</script>
</body>
</html>
"""


def _verd_map(verdicts):
    """[{tier,label,reason}] -> {tier: {label, reason}} for the page."""
    return {v["tier"]: {"label": v.get("label"), "reason": v.get("reason", "")}
            for v in (verdicts or []) if isinstance(v, dict) and "tier" in v}


def build(report: dict, audit: dict | None, src_name: str) -> str:
    # old-side labels come from the audit report (keyed by slug), if available
    old_by_slug = {}
    if audit:
        for r in audit.get("results", []):
            old_by_slug[r["slug"]] = (_verd_map(r.get("verdicts")), r.get("heuristic", {}))

    rows = []
    n_changed = n_keep = 0
    for r in report["results"]:
        ov, oh = old_by_slug.get(r["slug"], ({}, {}))
        outcome = r.get("outcome", "would")
        if outcome in ("wrote", "would"):
            n_changed += 1
        else:
            n_keep += 1
        rows.append({
            "slug": r["slug"], "outcome": outcome,
            "old": r.get("old", []), "new": r.get("new", []),
            "old_ct": r.get("old_ct"), "new_ct": r.get("new_ct"),
            "accepted": r.get("accepted", False),
            "new_flagged": r.get("new_flagged", []),
            "old_verdicts": ov, "old_heuristic": oh,
            "new_verdicts": _verd_map(r.get("new_verdicts")),
            "new_heuristic": r.get("new_heuristic", {}),
        })

    mode = "APPLY (written)" if report.get("apply") else "DRY RUN (nothing written)"
    meta = (f'{report["count"]} problems · {mode} · model {report.get("model","?")} · '
            f'{report.get("generated_at","?")} · changed {n_changed} / kept {n_keep}')
    return (PAGE
            .replace("__COUNT__", str(report["count"]))
            .replace("__META__", meta)
            .replace("__SRC__", src_name)
            .replace("__N_CHANGED__", str(n_changed))
            .replace("__N_KEEP__", str(n_keep))
            .replace("__DATA__", json.dumps(rows, ensure_ascii=False)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="read fix-apply.json (default: fix-dry.json)")
    ap.add_argument("-i", "--input", type=pathlib.Path, default=None,
                    help="explicit fix report path (overrides --apply)")
    ap.add_argument("-o", "--output", type=pathlib.Path, default=HINTS / "compare.html",
                    help=f"HTML output (default {HINTS / 'compare.html'})")
    ap.add_argument("--audit", type=pathlib.Path, default=HINTS / "audit.json",
                    help="audit report for old-side labels (optional)")
    ap.add_argument("--open", action="store_true", help="open the page in a browser when done")
    args = ap.parse_args()

    src = args.input or (HINTS / ("fix-apply.json" if args.apply else "fix-dry.json"))
    if not src.exists():
        print(f"ERROR: no fix report at {src}. Run:\n"
              f"  python scripts/improve_hints.py fix --from-report "
              f"{'--apply' if args.apply else '--dry-run'}")
        return 1
    report = json.loads(src.read_text(encoding="utf-8"))
    audit = json.loads(args.audit.read_text(encoding="utf-8")) if args.audit.exists() else None

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(report, audit, src.name), encoding="utf-8")
    print(f"Wrote {args.output}  ({args.output.stat().st_size//1024} KB, "
          f"{report['count']} problems from {src.name})")
    if args.open:
        webbrowser.open(args.output.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
