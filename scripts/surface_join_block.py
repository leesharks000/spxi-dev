#!/usr/bin/env python3
"""surface_join_block.py — bake "Read and composed" onto a fleet surface from alexanarch's capture join (2026-10-14).

Portable: one copy per surface repo, as spxi_instrument_label.py is. It reads the surface's own join file,
https://www.alexanarch.org/data/surface-joins/<domain>.json (or a local path), and writes server-delivered HTML between
the markers <!-- SURFACE-JOIN:BEGIN --> and <!-- SURFACE-JOIN:END --> (SPXI method 1.2). On a page without the markers
the block goes before --before (default: the first <footer>).

One row per observation: date, engine, address; the finding; a short excerpt of the response at the point the finding
concerns; links to the observation in its capture record, the /non entry and the paired observations. Every row
carries its obs_id. The block states its as-of date and registry version, so a stale block says so.

  python3 scripts/surface_join_block.py --domain spxi.dev --page index.html [--source PATH_OR_URL] [--limit 8]

Writes only when the block changed; exits 0 either way. A surface that removes the markers loses only the projection.
"""
import argparse, html, json, re, sys, urllib.request

BEGIN, END = "<!-- SURFACE-JOIN:BEGIN -->", "<!-- SURFACE-JOIN:END -->"
BASE = "https://www.alexanarch.org"
NOTICE = ("SPXI means inscription by discernment: a machine account of this entity may be held, with its sources, to discernment, "
          "accuracy, epistemic discipline and fairness, and kept as a dated, attributable record that a later account can be read against.")
VERDICT = {"distorts": "distorts", "represents_faithfully": "represents faithfully"}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def load(src):
    if re.match(r"https?://", src):
        with urllib.request.urlopen(src, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    with open(src, encoding="utf-8") as f:
        return json.load(f)


def row(r):
    anc = r["observation"]
    pairs = " · ".join(f'<a href="{esc(p["observation"])}"><code>{esc(p["obs_id"])}</code></a>' for p in r.get("pairs") or [])
    non = " · ".join(f'<a href="{BASE}/non/{esc(n)}/">/non {esc(n)}</a>' for n in r.get("non") or [])
    ex = r.get("excerpt") or ""
    tail = "" if ex.endswith((".", "!", "?")) else "…"
    out = [f'<li class="sj-row" data-obs-id="{esc(r["obs_id"])}" style="margin:0 0 1rem 0">',
           f'<div class="sj-head" style="font-family:var(--mono);font-size:.8em;color:var(--text-dim)">{esc(r.get("date"))} · {esc(r.get("engine"))}'
           f' · {esc(r.get("auth"))} · <a href="{esc(anc)}"><code>{esc(r["obs_id"])}</code></a></div>',
           f'<div class="sj-q" style="margin:.2rem 0">«{esc(r.get("q"))}»</div>']
    if r.get("finding"):
        out.append(f'<div class="sj-finding"><strong>Finding</strong> ({esc(VERDICT.get(r.get("verdict"), r.get("verdict")))}): {esc(r["finding"])}</div>')
    if ex:
        out.append(f'<div class="sj-excerpt"><strong>Response:</strong> “{esc(ex)}{tail}”</div>')
    links = [f'<a href="{esc(anc)}">the observation</a>'] + ([non] if non else []) + ([f"paired with {pairs}"] if pairs else [])
    out.append('<div class="sj-links" style="font-size:.85em;color:var(--text-dim)">' + " · ".join(links) + "</div></li>")
    return "".join(out)


def block(d, limit):
    rows = d.get("rows") or []
    shown = rows[:limit]
    more = (f' <a href="{BASE}/data/surface-joins/{esc(d["surface"])}.json">All {len(rows)} rows as data.</a>' if len(rows) > limit else "")
    return (f'{BEGIN}\n<section class="surface-join" id="read-and-composed" data-as-of="{esc(d.get("as_of"))}" '
            f'data-registry-version="{esc(d.get("registry_version"))}" style="padding:3rem 0 2rem;border-top:1px solid var(--border);margin-top:3rem">\n'
            f'<h2>Read and composed: what machine answers said, from or about this surface</h2>\n'
            f'<p style="color:var(--text-dim)"><em>{esc(NOTICE)}</em></p>\n'
            f'<p style="font-size:.85em;color:var(--text-dim)">As of {esc(d.get("as_of"))}, Capture Registry v{esc(d.get("registry_version"))}. '
            f'Each row is one observation, seated with its transcript at alexanarch.org; the finding is a reading, the excerpt is the answer\'s own words. '
            f'From <a href="{esc(d.get("source"))}">the capture join</a>.{more}</p>\n'
            '<ul style="list-style:none;padding:0">' + "\n".join(row(r) for r in shown) + "</ul>\n</section>\n" + END)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True)
    ap.add_argument("--page", default="index.html")
    ap.add_argument("--source")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--before", default="<footer>")
    a = ap.parse_args()
    d = load(a.source or f"{BASE}/data/surface-joins/{a.domain}.json")
    s = open(a.page, encoding="utf-8").read()
    b = block(d, a.limit)
    if BEGIN in s and END in s:
        new = s[: s.index(BEGIN)] + b + s[s.index(END) + len(END):]
    elif a.before in s:
        i = s.index(a.before)
        new = s[:i] + b + "\n" + s[i:]
    else:
        print(f"surface-join: no markers and no {a.before!r} in {a.page}; nothing written")
        return 0
    if new != s:
        open(a.page, "w", encoding="utf-8").write(new)
        print(f"surface-join: {a.page} written, {len(d.get('rows') or [])} rows, as of {d.get('as_of')}")
    else:
        print(f"surface-join: {a.page} unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
