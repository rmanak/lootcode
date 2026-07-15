#!/usr/bin/env python3
"""Render .hints/audit.json into a self-contained, browsable HTML page.

`improve_hints.py audit` writes a big JSON report; this turns it into a single
static HTML file you can open in a browser to eyeball flagged hints, read the
judge's reasoning per tier, filter by status/tier, and search by slug. No server,
no external assets — the report data is inlined, so the file works offline and can
be regenerated after every re-audit.

    python scripts/hint_audit_report.py                 # .hints/audit.json -> .hints/audit.html
    python scripts/hint_audit_report.py -o /tmp/h.html  # custom output
    python scripts/hint_audit_report.py --open          # ...and open it
"""
from __future__ import annotations

import argparse
import json
import pathlib
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_IN = ROOT / ".hints" / "audit.json"
DEFAULT_OUT = ROOT / ".hints" / "audit.html"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hint audit — __COUNT__ problems</title>
<style>
:root{
  --bg:#0f1216; --panel:#171b21; --panel2:#1e232b; --line:#2a313b;
  --fg:#e6e9ee; --dim:#9aa4b2; --faint:#6b7482;
  --leak:#f0616d; --vague:#e2b13c; --clean:#4fbf87; --none:#6b7482;
  --reveals:#f0616d; --ok:#4fbf87; --accent:#5aa0f0;
}
@media (prefers-color-scheme: light){
  :root{
    --bg:#f6f7f9; --panel:#fff; --panel2:#f0f2f5; --line:#dde1e7;
    --fg:#1a1f26; --dim:#5b6472; --faint:#8b94a2;
    --leak:#d63241; --vague:#b7860b; --clean:#1f9d5f; --none:#8b94a2;
    --reveals:#d63241; --ok:#1f9d5f; --accent:#2f6fd6;
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
code,.mono{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
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
.chip.leak.on{border-color:var(--leak);background:color-mix(in srgb,var(--leak) 16%,var(--panel2))}
.chip.vague.on{border-color:var(--vague);background:color-mix(in srgb,var(--vague) 16%,var(--panel2))}
.chip.clean.on{border-color:var(--clean);background:color-mix(in srgb,var(--clean) 16%,var(--panel2))}
input[type=search]{flex:1;min-width:180px;background:var(--panel2);border:1px solid var(--line);
  color:var(--fg);padding:6px 10px;border-radius:7px;font-size:13px}
label.toggle{display:flex;gap:5px;align-items:center;color:var(--dim);font-size:12.5px;cursor:pointer}
main{max-width:900px;margin:0 auto;padding:16px 20px 80px}
.count{color:var(--dim);font-size:12.5px;margin:4px 0 12px}
.card{background:var(--panel);border:1px solid var(--line);border-left-width:3px;
  border-radius:9px;padding:12px 14px;margin-bottom:10px}
.card.leak{border-left-color:var(--leak)}
.card.vague{border-left-color:var(--vague)}
.card.clean{border-left-color:var(--clean)}
.card.no-hints{border-left-color:var(--none)}
.card h2{margin:0;font-size:15px;display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.slug{font-family:ui-monospace,monospace}
.badge{font-size:10.5px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;
  padding:2px 7px;border-radius:5px;border:1px solid transparent}
.badge.leak{color:var(--leak);border-color:var(--leak)}
.badge.vague{color:var(--vague);border-color:var(--vague)}
.badge.clean{color:var(--clean);border-color:var(--clean)}
.badge.no-hints{color:var(--none);border-color:var(--none)}
.tiers{color:var(--faint);font-size:12px}
.hints{margin:10px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:7px}
.hint{display:grid;grid-template-columns:auto 1fr;gap:9px;padding:7px 9px;border-radius:7px;
  background:var(--panel2);border:1px solid transparent}
.hint.flag{border-color:color-mix(in srgb,var(--leak) 40%,var(--line))}
.hint.flag-vague{border-color:color-mix(in srgb,var(--vague) 45%,var(--line))}
.tier{font-weight:700;color:var(--faint);font-size:12px;white-space:nowrap}
.htext{font-size:13.5px}
.labels{display:flex;gap:5px;flex-wrap:wrap;margin-top:3px}
.lab{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.3px;
  padding:1px 6px;border-radius:4px}
.lab.reveals{color:#fff;background:var(--reveals)}
.lab.vague{color:#241c00;background:var(--vague)}
.lab.ok{color:var(--ok);border:1px solid var(--ok)}
.lab.regex{color:var(--dim);border:1px solid var(--line)}
.reason{color:var(--dim);font-size:12.5px;margin-top:3px;font-style:italic}
.empty{color:var(--faint);text-align:center;padding:40px}
footer{color:var(--faint);font-size:11.5px;text-align:center;padding:20px}
</style>
</head>
<body>
<header>
  <h1>Hint audit</h1>
  <div class="meta">__META__</div>
  <div class="controls">
    <span class="chip status leak"    data-status="leak">leak<span class="n">__N_LEAK__</span></span>
    <span class="chip status vague"   data-status="vague">vague<span class="n">__N_VAGUE__</span></span>
    <span class="chip status clean"   data-status="clean">clean<span class="n">__N_CLEAN__</span></span>
    <span class="chip status no-hints" data-status="no-hints">no-hints<span class="n">__N_NONE__</span></span>
    <input type="search" id="q" placeholder="filter by slug…" autocomplete="off">
    <label class="toggle"><input type="checkbox" id="tier3"> tier-3 only</label>
    <label class="toggle"><input type="checkbox" id="reveals"> judge&nbsp;“reveals”&nbsp;only</label>
  </div>
</header>
<main>
  <div class="count" id="count"></div>
  <div id="list"></div>
  <div class="empty" id="empty" hidden>No problems match.</div>
</main>
<footer>Generated from .hints/audit.json · leak/vague first, then by slug</footer>
<script>
const DATA = __DATA__;
const list = document.getElementById('list');
const countEl = document.getElementById('count');
const emptyEl = document.getElementById('empty');
const q = document.getElementById('q');
// default view: the actionable ones
const active = new Set(['leak','vague']);

document.querySelectorAll('.chip.status').forEach(ch=>{
  const s = ch.dataset.status;
  if(active.has(s)) ch.classList.add('on');
  ch.onclick = ()=>{ ch.classList.toggle('on');
    ch.classList.contains('on')?active.add(s):active.delete(s); render(); };
});
q.oninput = render;
document.getElementById('tier3').onchange = render;
document.getElementById('reveals').onchange = render;

function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}

function card(r){
  const verd = {}; (r.verdicts||[]).forEach(v=>verd[v.tier]=v);
  const heur = r.heuristic||{};
  const flagged = new Set(r.flagged||[]);
  const hints = (r.hints||[]).map((h,i)=>{
    const t=i+1, v=verd[t]||{}, lab=v.label||'—';
    const isFlag=flagged.has(t);
    const cls = isFlag ? (lab==='vague'?'flag-vague':'flag') : '';
    const labs = [];
    if(lab==='reveals') labs.push('<span class="lab reveals">reveals</span>');
    else if(lab==='vague') labs.push('<span class="lab vague">vague</span>');
    else if(lab==='ok') labs.push('<span class="lab ok">ok</span>');
    if(heur[t]) labs.push('<span class="lab regex" title="'+esc(heur[t])+'">regex</span>');
    const reason = (lab!=='ok'&&lab!=='—'&&v.reason)?'<div class="reason">'+esc(v.reason)+'</div>':'';
    return `<li class="hint ${cls}"><span class="tier">H${t}</span><div>
      <div class="htext">${esc(h)}</div>
      <div class="labels">${labs.join('')}</div>${reason}</div></li>`;
  }).join('');
  const tiers = (r.flagged&&r.flagged.length)?`<span class="tiers">tiers ${r.flagged.join(', ')}</span>`:'';
  return `<div class="card ${r.status}">
    <h2><span class="slug">${esc(r.slug)}</span>
      <span class="badge ${r.status}">${r.status}</span>${tiers}</h2>
    ${hints?`<ul class="hints">${hints}</ul>`:''}</div>`;
}

function order(a,b){
  const rank={leak:0,vague:1,clean:2,'no-hints':3};
  return (rank[a.status]-rank[b.status])||a.slug.localeCompare(b.slug);
}

function render(){
  const needle=q.value.trim().toLowerCase();
  const t3=document.getElementById('tier3').checked;
  const rev=document.getElementById('reveals').checked;
  let rows=DATA.filter(r=>active.has(r.status));
  if(needle) rows=rows.filter(r=>r.slug.toLowerCase().includes(needle));
  if(t3) rows=rows.filter(r=>(r.flagged||[]).includes(3));
  if(rev) rows=rows.filter(r=>(r.verdicts||[]).some(v=>v.label==='reveals'));
  rows.sort(order);
  countEl.textContent=`${rows.length} shown`;
  emptyEl.hidden=rows.length>0;
  list.innerHTML=rows.map(card).join('');
}
render();
</script>
</body>
</html>
"""


def build(report: dict) -> str:
    res = report["results"]
    counts = {"leak": 0, "vague": 0, "clean": 0, "no-hints": 0}
    for r in res:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    meta = (f'{report["count"]} problems · model {report.get("model","?")} · '
            f'{report.get("generated_at","?")} · '
            f'leak {counts["leak"]} / clean {counts["clean"]} / '
            f'vague {counts["vague"]} / no-hints {counts["no-hints"]}')
    # keep the payload lean: only fields the page reads
    slim = [{"slug": r["slug"], "status": r["status"], "hints": r.get("hints", []),
             "verdicts": r.get("verdicts", []), "heuristic": r.get("heuristic", {}),
             "flagged": r.get("flagged", [])} for r in res]
    return (PAGE
            .replace("__COUNT__", str(report["count"]))
            .replace("__META__", meta)
            .replace("__N_LEAK__", str(counts["leak"]))
            .replace("__N_VAGUE__", str(counts["vague"]))
            .replace("__N_CLEAN__", str(counts["clean"]))
            .replace("__N_NONE__", str(counts["no-hints"]))
            .replace("__DATA__", json.dumps(slim, ensure_ascii=False)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-i", "--input", type=pathlib.Path, default=DEFAULT_IN,
                    help=f"audit JSON (default {DEFAULT_IN})")
    ap.add_argument("-o", "--output", type=pathlib.Path, default=DEFAULT_OUT,
                    help=f"HTML output (default {DEFAULT_OUT})")
    ap.add_argument("--open", action="store_true", help="open the page in a browser when done")
    args = ap.parse_args()
    if not args.input.exists():
        print(f"ERROR: no report at {args.input}. Run: python scripts/improve_hints.py audit")
        return 1
    report = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(report), encoding="utf-8")
    print(f"Wrote {args.output}  ({args.output.stat().st_size//1024} KB, {report['count']} problems)")
    if args.open:
        webbrowser.open(args.output.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
