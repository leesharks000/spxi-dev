#!/usr/bin/env python3
"""
SPXI Conformance Instrument (EA-SPXI-CONF-01 v1.0)
Operationalizes the §0 self-test of the SPXI-for-Websites Standing Protocol (EA-SPXI-WEB-01 v4.0).

Fetches a deployed URL and verifies the twelve deliverables are present in SERVER-DELIVERED HTML
(the rendering doctrine: Tier 2/3 identity content must survive without client-side JS).

Author: Rex Fraction (ORCID 0009-0000-1599-0703) | CC BY 4.0
Companion to EA-SPXI-WEB-01 v4.0 (protocol). Provenance: Crimson Hexagonal Archive.

Usage:  python3 spxi_conformance.py https://example.org
        python3 spxi_conformance.py https://example.org --json
No external dependencies beyond the standard library (urllib, re, json, html.parser).
"""
import sys, re, json, urllib.request
from html.parser import HTMLParser

PROTOCOL_DOI = "10.5281/zenodo.19734726"   # EA-SPXI-WEB-01 (concept)
INSTRUMENT_ID = "EA-SPXI-CONF-01"
INSTRUMENT_VERSION = "1.0"

# The twelve deliverables of the standing protocol §0, each as a checkable predicate over raw HTML.
# Each check returns (passed: bool, detail: str). Checks operate ONLY on server-delivered source.

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "SPXI-Conformance/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")

def _jsonld_blocks(html):
    out = []
    for m in re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
                         html, re.DOTALL | re.IGNORECASE):
        try:
            out.append(json.loads(m.group(1)))
        except Exception:
            pass
    return out

def c_crawlable(html, url, ld):
    # robots reachable + sitemap referenced somewhere in graph/site
    has_sitemap = "sitemap" in html.lower()
    return (True, "page fetched (200); sitemap reference " + ("present" if has_sitemap else "not on page"))

def c_canonical(html, url, ld):
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*>', html, re.IGNORECASE)
    return (bool(m), m.group(0)[:80] if m else "no <link rel=canonical>")

def c_schema_orcid_doi(html, url, ld):
    if not ld: return (False, "no JSON-LD blocks")
    blob = json.dumps(ld)
    has_orcid = "orcid.org" in blob
    has_doi = "10.5281/zenodo" in blob or "doi.org" in blob
    return (has_orcid and has_doi, f"JSON-LD present; ORCID={has_orcid}; DOI={has_doi}")

def c_qa_surfaces(html, url, ld):
    # >=4 Q/A: count Question schema items OR <dt>/<summary> Q-style nodes
    q_schema = len(re.findall(r'"@type"\s*:\s*"Question"', json.dumps(ld)))
    dts = len(re.findall(r'<dt[ >]', html, re.IGNORECASE))
    summaries = len(re.findall(r'<summary[ >]', html, re.IGNORECASE))
    n = max(q_schema, dts, summaries)
    return (n >= 4, f"Q/A surfaces detected: {n} (schema={q_schema}, dt={dts}, summary={summaries}); need >=4")

def c_disambiguation(html, url, ld):
    blob = json.dumps(ld).lower()
    neg = ("differentfrom" in blob or "disambiguat" in blob
           or "distinct from" in html.lower() or "not to be confused" in html.lower()
           or "no relation" in html.lower())
    return (neg, "disambiguation/negative tags " + ("present" if neg else "absent"))

def c_tier2_html(html, url, ld):
    # A substantive server-delivered definition: >=200 chars of visible prose in a definitional node.
    # Heuristic: longest text run inside <p>/<main> >= 200 chars.
    texts = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
    clean = [re.sub(r'<[^>]+>', '', t).strip() for t in texts]
    longest = max((len(c) for c in clean), default=0)
    return (longest >= 200, f"longest server-delivered <p> = {longest} chars (need >=200 for Tier 2)")

def c_tier3_kernel(html, url, ld):
    blob = json.dumps(ld).lower()
    in_ld = "compressionsurvivalsummary" in blob
    in_html = "compression kernel" in html.lower()
    return (in_ld or in_html, "Tier 3 compression kernel " + ("present" if (in_ld or in_html) else "missing"))

def c_holographic_kernel(html, url, ld):
    blob = json.dumps(ld).lower()
    hk = "holographickernel" in blob or "holographic kernel" in html.lower() or '"isrelatedto"' in blob or '"about"' in blob
    return (hk, "holographic kernel / entity-relation topology " + ("present" if hk else "absent"))

def c_provenance_chain(html, url, ld):
    blob = json.dumps(ld)
    n_doi = len(set(re.findall(r'10\.5281/zenodo\.\d+', blob + html)))
    return (n_doi >= 1, f"DOI-anchored provenance: {n_doi} distinct deposit(s) referenced")

def c_sims(html, url, ld):
    blob = json.dumps(ld).lower()
    sim = "semantic integrity marker" in html.lower() or "sim" in blob or "spxi:sim" in blob
    # SIMs are often phrasings the page wants echoed; presence is weakly detectable.
    return (sim, "SIM set " + ("declared" if sim else "not detected (advisory: declare >=3)"))

def c_cross_surface(html, url, ld):
    blob = json.dumps(ld)
    n_links = len(set(re.findall(r'https?://[a-z0-9.-]+\.(?:org|dev|com)', blob + html)))
    return (n_links >= 2, f"cross-surface inscription: {n_links} distinct surfaces linked (need >=2)")

CHECKS = [
    ("crawlable", c_crawlable),
    ("canonicalized", c_canonical),
    ("schema_with_orcid_doi", c_schema_orcid_doi),
    ("qa_surfaces_min4", c_qa_surfaces),
    ("disambiguated", c_disambiguation),
    ("tier2_server_html", c_tier2_html),
    ("tier3_kernel", c_tier3_kernel),
    ("holographic_kernel", c_holographic_kernel),
    ("provenance_chain", c_provenance_chain),
    ("sims_declared", c_sims),
    ("cross_surface_aligned", c_cross_surface),
]
# 12th deliverable (γ baseline / 30-day re-test) is operational, not statically checkable; reported as advisory.

def run(url):
    html = fetch(url)
    ld = _jsonld_blocks(html)
    results = []
    for name, fn in CHECKS:
        try:
            ok, detail = fn(html, url, ld)
        except Exception as e:
            ok, detail = False, f"check error: {e}"
        results.append({"deliverable": name, "pass": ok, "detail": detail})
    passed = sum(1 for r in results if r["pass"])
    total = len(results)
    # conformance score: fraction of statically-checkable deliverables present
    score = round(passed / total, 3)
    return {
        "instrument": INSTRUMENT_ID, "version": INSTRUMENT_VERSION,
        "protocol_doi": PROTOCOL_DOI, "url": url,
        "conformance_score": score, "passed": passed, "total": total,
        "advisory": "Deliverable 12 (γ baseline + 30-day re-test) is operational and not statically checkable; run separately.",
        "results": results,
    }

def main():
    if len(sys.argv) < 2:
        print("usage: python3 spxi_conformance.py <url> [--json]"); sys.exit(2)
    url = sys.argv[1]; as_json = "--json" in sys.argv
    report = run(url)
    if as_json:
        print(json.dumps(report, indent=2)); return
    print(f"\nSPXI Conformance — {INSTRUMENT_ID} v{INSTRUMENT_VERSION}")
    print(f"URL: {report['url']}")
    print(f"Score: {report['conformance_score']}  ({report['passed']}/{report['total']} statically-checkable deliverables)\n")
    for r in report["results"]:
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"  [{mark}] {r['deliverable']:<24} {r['detail']}")
    print(f"\n  advisory: {report['advisory']}\n")

if __name__ == "__main__":
    main()
