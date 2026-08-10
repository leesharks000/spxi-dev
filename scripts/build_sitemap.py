#!/usr/bin/env python3
"""build_sitemap.py — the sitemap generated from the repository, not typed.

Every hand-maintained sitemap drifts. This one had complete coverage and six of
eight lastmod dates stale by three days, because the nav rewrite touched every page
and nothing updated the dates. Coverage was right and freshness was wrong, which is
the failure a person checking "is it current?" is least likely to see.

Pages come from the filesystem; lastmod comes from git's last commit touching that
file. Priority is declared here once, because it is editorial judgement rather than
a fact about the repository.

    python3 scripts/build_sitemap.py
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
HOST = "https://spxi.dev"

PRIORITY = {
    "/": "1.0",
    "/what-is-spxi/": "0.9",
    "/how-it-works/": "0.9",
    "/analog/": "0.8",
    "/analog/artifacts/": "0.8",
    "/analog/advance/": "0.8",
    "/tlp/": "0.8",
    "/conformance/": "0.8",
    "/standing-protocol/": "0.8",
    "/disambiguation/": "0.7",
    "/analog/v1.0/": "0.2",
}
DEFAULT = "0.6"


def route(p):
    rel = p.parent.relative_to(ROOT)
    return "/" if str(rel) == "." else f"/{rel}/"


def lastmod(p):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ad", "--date=short", "--", str(p.relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return out or "1970-01-01"


def main():
    pages = sorted((p for p in ROOT.rglob("index.html") if ".git" not in str(p)),
                   key=lambda p: (route(p) != "/", route(p)))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        r = route(p)
        lines.append(f"  <url><loc>{HOST}{r}</loc><lastmod>{lastmod(p)}</lastmod>"
                     f"<priority>{PRIORITY.get(r, DEFAULT)}</priority></url>")
    lines.append("</urlset>")
    out = "\n".join(lines) + "\n"
    (ROOT / "sitemap.xml").write_text(out, encoding="utf-8")

    print(f"  {len(pages)} pages")
    for p in pages:
        print(f"    {lastmod(p)}  {PRIORITY.get(route(p), DEFAULT)}  {route(p)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
