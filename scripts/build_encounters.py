#!/usr/bin/env python3
"""build_encounters.py — SPXI encounters, as complete records with consequences (DRAFT, 2026-10-14).

An encounter: a composing system answers about an entity; its answer, the source it was answering, the finding and
the correction are each held as an attributable object, and a later encounter can inspect the history. The four
criteria (Lee Sharks, 2026-10-14: discernment, accuracy, epistemic discipline, fairness) are shown by what each lets
someone do with the encounter: distinguish, establish, challenge, preserve.

Nothing here is retyped. Each page is generated from records already seated on alexanarch.org:
  the capture record      /captures/<slug>/record.json         (transcript, surface, sign-in, PER)
  the /non row            /datasets/negative-of-the-negative/v2/rows/<entity>.json   (negative: exhibit, moves N1..Nn,
                          answered_by, KO_sentences, P_items, check; objects.KO sentences; objects.P compression)
  the /non ledger         the row's ledger.archive path        (claims with quote, locus, deposit)
  the registry index      /captures/index.json                 (later observations at the entity's addresses)
The only thing declared below is the reading of each move: which criterion it fails and which instrument holds it.

Usage: python3 scripts/build_encounters.py [--alexanarch /path/to/clone]   (writes encounters/<slug>/index.html,
encounters/index.html, encounters.json). Without --alexanarch the records are fetched from www.alexanarch.org.
"""
import html, json, pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
AX = "https://www.alexanarch.org"
LOCAL = pathlib.Path(sys.argv[sys.argv.index("--alexanarch") + 1]) if "--alexanarch" in sys.argv else None

CRIT = {"D": ("discernment", "distinguish"), "A": ("accuracy", "establish"),
        "E": ("epistemic discipline", "challenge"), "F": ("fairness", "challenge")}

# entity row → per-move reading: (criteria, instruments that hold the move)
ENCOUNTERS = {
    "spxi": {
        "N1": ("D", [("Method inventory, spxi.dev/methods", "https://www.spxi.dev/methods/"), ("the extension in its place: method 4.1", "https://www.spxi.dev/methods/#m-4-1")]),
        "N2": ("AF", [("PER on the capture (PER-M, PER-C, PER-D)", "https://www.spxi.dev/methods/#m-0-6"), ("Erasure Skew Ω: whom the loss falls on", AX + "/s/records/157/")]),
        "N3": ("E", [("Claim Status Packet: a specification's state carried as data", "https://www.spxi.dev/methods/#m-3-9")]),
        "N4": ("F", [("The evidentiary standard: evidence, not the standing of the claimant", "https://www.spxi.dev/methods/#m-7-6")]),
        "N5": ("EF", [("The inventory's rule: a caveat is stated with what was inspected to produce it", "https://www.spxi.dev/methods.json"), ("The evidentiary standard", "https://www.spxi.dev/methods/#m-7-6")]),
        "N6": ("D", [("Disambiguation Matrix: the near neighbours it is not", "https://www.spxi.dev/methods/#m-3-4")]),
        "N7": ("E", [("Capture Registry: both turns held verbatim, so the withdrawal is on the record beside what it withdrew", "https://www.spxi.dev/methods/#m-0-9")]),
        "N8": ("FD", [("The Trusted Intermediary (#1638)", AX + "/s/records/1638/"), ("Directionality of Semantic Labor: what the response did with the task it was given (not yet run on this encounter)", "https://www.laborvector.org/")]),
        "N9": ("D", [("Method inventory, spxi.dev/methods", "https://www.spxi.dev/methods/")]),
    },
}


def get(path):
    if LOCAL and (LOCAL / path.lstrip("/")).exists():
        return json.loads((LOCAL / path.lstrip("/")).read_text(encoding="utf-8"))
    with urllib.request.urlopen(AX + "/" + path.lstrip("/"), timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


e = html.escape
HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link rel="canonical" href="{canon}">
<title>{title} — SPXI</title>
<meta content="{desc}" name="description"/>
<meta content="index, follow" name="robots"/>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&amp;family=IBM+Plex+Sans:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
<script type="application/ld+json">{ld}</script>
<link rel="stylesheet" href="/assets/type.css">
<style>
  :root {{ --bg:#0a0a0c; --surface:#111114; --border:#1e1e24; --text:#e8e6e3; --text-dim:#8a8a8e; --accent:#c23d2e; --gold:#c9a227; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:var(--sans, 'IBM Plex Sans', sans-serif); background:var(--bg); color:var(--text); line-height:1.7; }}
  .container {{ max-width:760px; margin:0 auto; padding:48px 20px; }}
  header {{ padding-bottom:28px; border-bottom:1px solid var(--border); margin-bottom:28px; }}
  header a, .eyebrow {{ color:var(--text-dim); text-decoration:none; font-family:var(--mono, 'IBM Plex Mono', monospace); font-size:.8rem; letter-spacing:.06em; }}
  h1 {{ font-size:1.7rem; font-weight:300; margin:.6rem 0 .4rem; }} h1 em {{ color:var(--accent); font-style:normal; }}
  h2 {{ font-family:var(--mono, monospace); font-size:.85rem; font-weight:500; color:var(--text-dim); text-transform:uppercase; letter-spacing:.06em; margin:2.6rem 0 .8rem; }}
  p {{ margin:.8rem 0; font-size:.95rem; }} a {{ color:var(--gold); }}
  .facts {{ font-family:var(--mono, monospace); font-size:.82rem; color:var(--text-dim); border-left:3px solid var(--accent); padding:.6rem .9rem; background:var(--surface); }}
  .facts b {{ color:var(--text); font-weight:500; }}
  .move {{ border:1px solid var(--border); background:var(--surface); border-radius:4px; padding:1rem 1.1rem; margin:1.1rem 0; scroll-margin-top:20px; }}
  .move .id {{ font-family:var(--mono, monospace); color:var(--accent); font-weight:600; margin-right:.5rem; }}
  .chip {{ display:inline-block; font-family:var(--mono, monospace); font-size:.7rem; letter-spacing:.05em; text-transform:uppercase; border:1px solid var(--gold); color:var(--gold); border-radius:3px; padding:0 .4rem; margin-right:.3rem; }}
  blockquote {{ margin:.7rem 0; padding:.2rem 0 .2rem .9rem; border-left:2px solid var(--text-dim); color:#d6d3cf; font-style:italic; }}
  .type {{ font-size:.88rem; color:var(--text-dim); }}
  .k {{ font-family:var(--mono, monospace); font-size:.72rem; letter-spacing:.06em; text-transform:uppercase; color:var(--text-dim); margin-top:.8rem; }}
  ul {{ margin:.3rem 0 .3rem 1.1rem; font-size:.9rem; }} li {{ margin:.25rem 0; }}
  .src q {{ color:#d6d3cf; }} .loc {{ color:var(--text-dim); font-size:.82rem; }}
  .ok {{ color:#7fb77e; font-family:var(--mono, monospace); font-size:.8rem; }}
  table {{ width:100%; border-collapse:collapse; font-size:.86rem; margin:.6rem 0; }} td, th {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--border); vertical-align:top; }}
  th {{ font-family:var(--mono, monospace); font-size:.72rem; color:var(--text-dim); text-transform:uppercase; letter-spacing:.05em; font-weight:500; }}
  footer {{ margin-top:3rem; padding-top:1rem; border-top:1px solid var(--border); color:var(--text-dim); font-family:var(--mono, monospace); font-size:.78rem; }}
  @media (max-width:560px) {{ .container {{ padding:32px 16px; }} h1 {{ font-size:1.4rem; }} }}
.sitenav{{display:flex;gap:0;flex-wrap:wrap;align-items:baseline;font-family:var(--mono);
font-size:var(--fs-micro);letter-spacing:var(--tr-wide);text-transform:uppercase;
border-bottom:1px solid var(--border,#1e1e24);margin:0 0 2rem;padding:14px 0 10px}}
.sitenav .wm{{color:var(--accent,#c23d2e);text-decoration:none;font-weight:600;
margin-right:auto;letter-spacing:.24em}}
.sitenav a{{color:var(--text-dim,#8a8a8e);text-decoration:none;padding:3px 11px;
border-left:1px solid var(--border,#1e1e24)}}
.sitenav a:hover{{color:var(--text,#e8e6e3)}}
.sitenav a.here{{color:var(--accent,#c23d2e)}}
.sitenav a:first-of-type{{border-left:0}}
@media(max-width:640px){{.sitenav{{font-size:9px}}.sitenav a{{padding:3px 7px}}}}
</style>
</head>
<body>
<nav class="sitenav" aria-label="SPXI"><a class="wm" href="/">SPXI</a><a href="/what-is-spxi">What</a><a href="/how-it-works">How</a><a href="/methods">Methods</a><a href="/analog">Analog</a><a href="/tlp">TLP</a><a href="/conformance">Conformance</a><a href="/encounters" class="here">Encounters</a><a href="/standing-protocol">Apply</a><a href="/disambiguation">Disambiguation</a><a href="/who/fraction">Who</a><a href="/where">Where</a></nav>
<div class="container">
<header><a href="/">← spxi.dev</a> · <a href="/encounters">encounters</a></header>
"""
FOOT = """<footer>SPXI encounters · generated from records seated at alexanarch.org; nothing on this page is retyped · Semantic Economy Institute · CC BY 4.0 · DRAFT</footer>
</div>
</body>
</html>
"""


def build(entity, reading):
    row = get(f"datasets/negative-of-the-negative/v2/rows/{entity}.json")
    neg = row["negative"]; ex = neg["exhibit"]; slug = ex["slug"]
    cap = get(f"captures/{slug}/record.json")
    led = get(row["ledger"]["archive"])
    claims = {c["id"]: c for c in (led["claims"] if isinstance(led, dict) else led)}
    KO = {s["n"]: s for s in row["objects"]["KO"]["sentences"]}
    P = row["objects"]["P"]
    plines = {}
    for sec in P["sections"]:
        for it in sec["items"]:
            plines[f'{sec["head"]} · {it["label"]}'] = it["text"]
    plines["lede"] = P["lede"]["text"] if isinstance(P["lede"], dict) else str(P["lede"])
    cap_url = ex["record"]; non_url = f"{AX}/non/{entity}/"; row_url = f"{AX}/datasets/negative-of-the-negative/v2/rows/{entity}.json"
    pv = cap.get("per_v") or {}

    moves, data_moves = [], []
    for m in neg["corrections"]:
        cs, inst = reading[m["id"]]
        chips = "".join(f'<span class="chip">{e(CRIT[c][0])}</span>' for c in cs)
        srcs = []
        for cid in m["answered_by"]:
            c = claims.get(cid)
            if not c:
                srcs.append(f"<li>{e(cid)} (not in ledger)</li>"); continue
            dep = c.get("dep")
            href = (c.get("surface") or {}).get("url") if isinstance(c.get("surface"), dict) else None
            href = href or (f"{AX}/s/records/{dep}/" if str(dep).isdigit() else None)
            label = f"#{dep}" if str(dep).isdigit() else str(dep)
            where = f'<a href="{e(href)}">{e(label)}</a>' if href else e(label)
            quote = (c.get("quote") or c.get("claim") or "").replace("**", "")  # markdown residue from the source copy; the words are the content
            srcs.append(f'<li class="src"><q>{e(quote)}</q> <span class="loc">— {where}, {e(c.get("locus") or "")} ({e(cid)})</span></li>')
        kos = "".join(f'<li>{e(KO[n]["text"])} <span class="loc">(sentence {n})</span></li>' for n in m["KO_sentences"] if n in KO)
        ps = "".join(f'<li>{e(p)} {e(plines.get(p, ""))}</li>' for p in m["P_items"] if p != "lede") + \
             ('<li>lede: ' + e(plines["lede"]) + '</li>' if "lede" in m["P_items"] else "")
        ins = "".join(f'<li><a href="{e(u)}">{e(n)}</a></li>' for n, u in inst)
        moves.append(f'''<div class="move" id="{e(m["id"].lower())}"><div><span class="id">{e(m["id"])}</span>{chips}</div>
<blockquote>{e(m["span"])}</blockquote>
<div class="type">{e(m["type"])}</div>
<div class="k">held by</div><ul>{ins}</ul>
<div class="k">the source says</div><ul>{"".join(srcs)}</ul>
<div class="k">corrected in the /non entry</div><ul>{kos}</ul><ul>{ps}</ul>
<div class="ok">corrective check: {e(m["check"])}</div></div>''')
        data_moves.append({"id": m["id"], "span": m["span"], "type": m["type"], "criteria": [CRIT[c][0] for c in cs],
                           "held_by": [{"name": n, "url": u} for n, u in inst], "answered_by": m["answered_by"],
                           "KO_sentences": m["KO_sentences"], "P_items": m["P_items"], "check": m["check"]})

    by = {}
    for dm in data_moves:
        for c in dm["criteria"]:
            by.setdefault(c, []).append(dm["id"])
    verbs = {"discernment": "distinguish", "accuracy": "establish", "epistemic discipline": "challenge", "fairness": "challenge"}
    crit_rows = "".join(f'<tr><td>{e(c)}</td><td>{e(verbs[c])}</td><td>{", ".join(f"<a href=#{i.lower()}>{i}</a>" for i in by.get(c, []))}</td></tr>'
                        for c in ("discernment", "accuracy", "epistemic discipline", "fairness"))

    idx = get("captures/index.json")
    rec = [r for r in idx.get("records", idx.get("addresses", [])) if isinstance(r, dict) and "spxi" in (r.get("q") or r.get("address") or "").lower()]
    rec.sort(key=lambda r: (r.get("dates") or [""])[0])
    here = lambda r: ' <span class="chip">this encounter</span>' if r.get("slug") == slug else ""
    returns = "".join(f'<tr><td>{e(", ".join(r.get("dates") or []))}</td><td><a href="{e(r.get("record_url") or "")}">{e(r.get("q") or "")}</a>{here(r)}</td><td>{e(", ".join(r.get("surfaces") or []))}</td><td>{e((r.get("status") or "").capitalize() if (r.get("status") or "").isupper() else (r.get("status") or ""))}</td></tr>' for r in rec)

    title = f'An encounter: “{ex["address"]}”, {ex["surface"]}, {ex["date"]}'
    canon = f"https://www.spxi.dev/encounters/{slug}"
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "@id": canon + "#encounter", "name": title,
          "additionalType": "SPXI encounter", "url": canon, "creativeWorkStatus": "Draft",
          "about": {"@type": "CreativeWork", "@id": cap_url, "name": f'{ex["surface"]} response at “{ex["address"]}”, {ex["date"]}'},
          "isBasedOn": [{"@id": cap_url}, {"@id": row_url}, {"@id": non_url}],
          "publisher": {"@type": "Organization", "name": "Semantic Economy Institute"},
          "author": {"@type": "Person", "name": "Lee Sharks", "identifier": "https://orcid.org/0009-0000-1599-0703"}}
    body = [HEAD.format(canon=e(canon), title=e(title), desc=e(f'A {ex["surface"]} answer about SPXI, its source, the findings and the corrections, each held as an attributable record.'), ld=json.dumps(ld, ensure_ascii=False))]
    body.append(f'''<div class="eyebrow">SPXI ENCOUNTER · {e(ex["surface"])} · {e(ex["date"])} · {e(ex["auth"])}</div>
<h1>“{e(ex["address"])}”</h1>
<p>A composing system was asked about SPXI. Its answer, the source it was answering, each finding and each correction are held here as attributable records with dates, so the answer has a source, a scope and a future in which someone can examine it.</p>
<div class="facts"><b>The response</b> · <a href="{e(cap_url)}">capture record</a>, transcript verbatim (<a href="{e(cap_url)}record.json">as data</a>) · <b>finding</b> {e(cap.get("mt") or "")}<br>
<b>PER</b> {e(str(cap.get("per")))}: author {"kept" if pv.get("author") else "lost"}, institution {"kept" if pv.get("inst") else "lost"}, identifier {"kept" if pv.get("id") else "lost"}, sources {"kept" if pv.get("src") else "lost"} · {e(cap.get("per_note") or "")}<br>
<b>corrected by</b> <a href="{e(non_url)}">/non {e(entity)}</a> · <b>check</b> {neg["check"]["answered"]} of {neg["check"]["of"]} answered</div>
<h2>What each criterion lets someone do here</h2>
<table><tr><th>criterion</th><th>lets someone</th><th>moves</th></tr>{crit_rows}<tr><td>inscription</td><td>preserve</td><td>every move: the response, the source, the finding and the correction, each at its own address</td></tr></table>
<h2>The moves</h2>
{"".join(moves)}
<h2>Preserved</h2>
<ul><li><a href="{e(cap_url)}">the response</a>: the semantic address, the date, the surface, the sign-in state, the transcript</li>
<li><a href="{e(row_url)}">the reading</a>: each move quoted, typed and answered; the check</li>
<li><a href="{e(AX + "/" + row["ledger"]["archive"])}">the source</a>: {len(claims)} claims, each with its quote, locus and deposit</li>
<li><a href="{e(non_url)}">the correction</a>: the /non entry's knowledge object and compression</li></ul>
<h2>Returns: every observation at an SPXI address</h2>
<p>A later encounter is read against this one: same address or a neighbour, a dated observation each.</p>
<table><tr><th>date</th><th>address</th><th>surface</th><th>finding</th></tr>{returns}</table>
''')
    body.append(FOOT)
    out = ROOT / "encounters" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(body), encoding="utf-8")
    return {"slug": slug, "url": canon, "entity": entity, "address": ex["address"], "surface": ex["surface"], "date": ex["date"],
            "auth": ex["auth"], "response": cap_url, "reading": row_url, "correction": non_url, "per": cap.get("per"),
            "check": neg["check"], "moves": data_moves, "returns": len(rec)}


recs = [build(k, v) for k, v in ENCOUNTERS.items()]
(ROOT / "encounters.json").write_text(json.dumps({"name": "SPXI encounters", "status": "DRAFT", "encounters": recs}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
items = "".join(f'<li><a href="/encounters/{e(r["slug"])}">“{e(r["address"])}”</a>, {e(r["surface"])}, {e(r["date"])}: {len(r["moves"])} moves, check {r["check"]["answered"]} of {r["check"]["of"]}</li>' for r in recs)
ld = {"@context": "https://schema.org", "@type": "CollectionPage", "@id": "https://www.spxi.dev/encounters", "name": "SPXI encounters", "creativeWorkStatus": "Draft"}
(ROOT / "encounters" / "index.html").write_text(HEAD.format(canon="https://www.spxi.dev/encounters", title="SPXI encounters", desc="Machine answers about SPXI-inscribed entities, each held with its source, findings and corrections.", ld=json.dumps(ld)) +
    f'<div class="eyebrow">SPXI ENCOUNTERS</div><h1>Encounters</h1><p>A machine answers about an entity. The answer, the source it was answering, the finding and the correction are each kept as a dated, attributable record, and the next answer can be read against them.</p><ul>{items}</ul>' + FOOT, encoding="utf-8")
for r in recs:
    print(r["slug"], len(r["moves"]), "moves;", r["returns"], "observations at SPXI addresses")
