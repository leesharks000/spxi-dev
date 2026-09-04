# SPXI

SPXI — Semantic Packet for eXchange & Indexing. Protocol specification surface. Rex Fraction, Semantic Economy Institute.

**Live:** https://spxi.dev/


---

Canonical records at [alexanarch.org](https://www.alexanarch.org/), content-addressed by [AXN](https://axnidentifiers.org/) — a changed text is a changed address. Harvest via [OAI-PMH](https://www.alexanarch.org/oai?verb=Identify).

## One URL grammar (2026-09-04)
Canonical form `https://www.spxi.dev/<path>`, no trailing slash (vercel `trailingSlash:false`). `scripts/url_grammar.py` rewrites canonicals/og/JSON-LD/links and derives `sitemap.xml` from the tree (`--check`); the older `scripts/build_sitemap.py` now points at www but emits trailing slashes and should not be used for the sitemap.
