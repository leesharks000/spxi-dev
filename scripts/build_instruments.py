#!/usr/bin/env python3
"""build_instruments.py — which surfaces carry which SPXI method, as data (2026-10-14).

spxi.dev/methods.json itemizes SPXI's 85 methods. Several are instruments that live on other surfaces (the Capture
Registry on alexanarch.org and its windows, the Provenance Erasure Rate on provenanceerasure.org, the Semantic
Addresses Framework, the PID Erosion Observatory). Until now the claim ran one way: the inventory named them, and
they did not name it. This script writes instruments.json, the single source each of those surfaces reads to label
itself an SPXI instrument (scripts/spxi_instrument_label.py, copied into each surface's repository with this file).

The method rows (id, name, level) are read from methods.json and never restated here; only the surface map is
declared below. Usage: python3 scripts/build_instruments.py   (writes instruments.json)
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "methods.json").read_text(encoding="utf-8"))
ITEMS = {it["id"]: (L, it) for L in M["spxi:levels"] for it in L["items"]}

# method id → the surfaces that carry it (URL prefixes), with a note where the surface also belongs elsewhere
SURFACES = {
    "0.6": [{"surface": "https://www.provenanceerasure.org/", "note": "The Provenance Erasure Rate is also the Semantic Economy's measure of provenance loss."}],
    "0.8": [{"surface": "https://www.alexanarch.org/addresses/"}],
    "0.9": [{"surface": "https://www.alexanarch.org/captures/"},
            {"surface": "https://www.machinemediation.org/captures/", "also": ["6.14"]},
            {"surface": "https://www.leesharks.com/captures/", "also": ["6.14"]},
            {"surface": "https://www.godkinggoogle.com/captures/", "also": ["6.14"]}],
    "0.10": [{"surface": "https://www.spxi.dev/conformance"}],
    "0.15": [{"surface": "https://www.persistentidentifiers.org/", "also": ["7.9"]}],
    "0.16": [{"surface": "https://www.alexanarch.org/non/"}],
    "0.17": [{"surface": "https://gnosis.spxi.dev/", "also": ["0.16"]}],
    "5.4": [{"surface": "https://www.spxi.dev/canary-registry"}],
}


def anchor(mid):
    return "https://www.spxi.dev/methods/#m-" + mid.replace(".", "-")


out = {"name": "SPXI instruments: the methods of spxi.dev/methods carried on other surfaces",
       "inventory": "https://www.spxi.dev/methods/", "inventory_data": "https://www.spxi.dev/methods.json",
       "itemCount": M.get("spxi:itemCount"), "levelCount": M.get("spxi:levelCount"),
       "rule": "A surface listed here labels itself, visibly and in its machine-readable head, with the method it carries, its level and a link to its row in the inventory. 'Instrument of' is kept apart from 'treated by': the SPXI-TLP layer a surface also carries says how it was built, the instrument label says what it is.",
       "instruments": []}
for mid, surfs in SURFACES.items():
    L, it = ITEMS[mid]
    out["instruments"].append({"method": mid, "name": it["name"], "what": it["what"], "source": it.get("source"),
                               "level": L["level"], "level_name": L["name"], "url": anchor(mid),
                               "surfaces": [dict(s, also=[{"method": a, "name": ITEMS[a][1]["name"], "url": anchor(a)} for a in s.get("also", [])]) for s in surfs]})
(ROOT / "instruments.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("instruments.json:", ", ".join(f'{i["method"]} → {len(i["surfaces"])}' for i in out["instruments"]))
