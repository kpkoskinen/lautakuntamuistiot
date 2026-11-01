#!/usr/bin/env python3
"""
Build a uMap (umap.openstreetmap.fr) map file from the same datasets as build_kml.
No network — pure render.

    python3 -m lautakuntamuistiot.build_umap                       # all records -> helsinki_plans.umap
    python3 -m lautakuntamuistiot.build_umap --years 2020-2026 -o recent.umap

The output is uMap's own export format (.umap: GeoJSON layers plus the map's
settings), so one import gives the whole map: one coloured layer per plan type
plus the Kerro kantasi layer, popups, a stage and year filter, centre and licence.
uMap imports KML too, but only as data, without these settings.

Each pin's popup is its `description`, written in uMap's own markup (**bold**,
*italic*, [[url|text]] links). The facts are also plain properties (date, year,
stage, plan_type, location, drawing_url, decision_url, ...), so they show in
uMap's table view and can be used in filters or a custom popup template.

Pins are deduped and declustered exactly as in build_kml.
"""
import argparse, json, os

from .build_kml import (KK_DATASET, LABEL, ORDER, SHORT, _dist_m, decluster,
                        dedupe_records, parse_years)
from .common import DATASET, STAGES, plan_stage
from .settings import OUT

# the KML paddle colours, as uMap colours
COLOR = {"katu": "#d7301f", "liikenne": "#2b6cd6", "puisto": "#1a9850",
         "asemakaava": "#e6b400", "muu_k": "#e7298a", "kerrokantasi": "#7b3fbf"}
CENTER = [24.94, 60.19]                                  # lon, lat — Helsinki
ATTRIBUTION = ("Decisions: City of Helsinki (paatokset.hel.fi), Kerro kantasi; "
               "locations geocoded with Nominatim, © OpenStreetMap contributors (ODbL). "
               "Experimental, heuristically extracted: pins are approximate.")


def _text(s):
    """Plain text for uMap markup: no accidental bold/italic, links or templates."""
    return (s or "").replace("*", "∗").replace("[[", "[ [").replace("{", "(").replace("}", ")")


def feature(r, pos=None):
    lon, lat = pos or (r["lon"], r["lat"])
    kk = r["plan_type"] == "kerrokantasi"
    stage = r.get("stage") or plan_stage(r)
    lines = [f'**{_text(r["heading"])}**',
             f'Comment period: {r["date"]}–{r.get("close_date") or "?"}' if kk
             else f'Decision date: {r["date"]} — {STAGES[stage]}']
    if r.get("summary"):
        lines.append(f'*{_text(r["summary"])}*')
    if kk:
        lines += [f'[[{u}|{_text(n)}]]' for n, u in r.get("drawings", [])]
        lines.append(f'[[{r["decision_url"]}|Kerro kantasi page]]')
    else:
        if r.get("map_url"):
            lines.append(f'[[{r["map_url"]}|Open plan drawing (PDF)]]')
        lines.append(f'[[{r["decision_url"]}|Decision page]]')
    moved = _dist_m(r["lon"], r["lat"], lon, lat)
    lines.append(f'Location: {_text(r["location"])}, approx: {r.get("geocode", "?")}-level'
                 + (f'; pin offset {moved:.0f} m to avoid overlap' if moved >= 1 else ''))
    props = {
        "name": f'{r["location"]} – {SHORT.get(r["plan_type"], r["plan_type"])} '
                f'{r["month"]:02d}/{r["year"]}',
        "description": "\n".join(lines),
        "date": r["date"], "year": r["year"], "stage": stage,
        "plan_type": r["plan_type"], "location": r["location"],
        "geocode": r.get("geocode"), "asia_id": r["asia_id"],
        "decision_url": r["decision_url"],
    }
    if r.get("map_url"):
        props["drawing_url"] = r["map_url"]
    if kk and r.get("close_date"):
        props["close_date"] = r["close_date"]
    return {"type": "Feature", "properties": props,
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]}}


def build(records, title, out, dedupe=True, min_sep=40.0, extra=()):
    if dedupe:
        records = dedupe_records(records)
    records = list(records) + list(extra)
    pos = decluster(records, min_sep) if min_sep > 0 else {}
    bytype = {k: [] for k in ORDER}
    for r in records:
        bytype.setdefault(r["plan_type"], []).append(r)
    layers = []
    for k in ORDER:
        recs = sorted(bytype.get(k, []), key=lambda r: (r["year"], r["month"]))
        layers.append({
            "type": "FeatureCollection",
            "features": [feature(r, pos.get(id(r))) for r in recs],
            "properties": {"name": f"{LABEL[k]} ({len(recs)})", "color": COLOR[k],
                           "iconClass": "Circle", "displayOnLoad": True,
                           "browsable": True, "inCaption": True},
        })
    doc = {
        "type": "umap",
        "properties": {
            "name": title,
            "description": ("Helsinki committee plan decisions and Kerro kantasi consultations, "
                            "one layer per plan type. " + ATTRIBUTION),
            "shortCredit": "Data: City of Helsinki, © OpenStreetMap contributors (ODbL)",
            "zoom": 12, "popupShape": "Large",
            "fields": [{"key": "name", "type": "String"},
                       {"key": "description", "type": "Text"},
                       {"key": "stage", "type": "String"},
                       {"key": "year", "type": "Number"}],
            "filters": [{"fieldKey": "stage", "widget": "Checkbox", "label": "Stage"},
                        {"fieldKey": "year", "widget": "MinMax", "label": "Year"}],
            "onLoadPanel": "caption",
        },
        "geometry": {"type": "Point", "coordinates": CENTER},
        "layers": layers,
    }
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    n = sum(len(bytype.get(k, [])) for k in ORDER)
    print(f"  {os.path.basename(out):28} {n:4} pins  "
          + " ".join(f"{k}:{len(bytype.get(k, []))}" for k in ORDER))
    return n


def main():
    ap = argparse.ArgumentParser(prog="python3 -m lautakuntamuistiot.build_umap",
                                 description="Build a uMap (.umap) map file from the datasets.")
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--years", default=None, help="e.g. 2025 | 2017-2026 | 2019,2021")
    ap.add_argument("--no-dedupe", action="store_true",
                    help="keep every decision as its own pin (default: one per asia+type)")
    ap.add_argument("--min-sep", type=float, default=40.0,
                    help="minimum metres between pins; overlapping ones are spread out (0 = off)")
    ap.add_argument("--kerrokantasi", default=KK_DATASET,
                    help="Kerro kantasi consultations dataset, added as its own layer "
                         "if the file exists ('' = leave out)")
    ap.add_argument("-o", "--out", default=f"{OUT}/helsinki_plans.umap")
    args = ap.parse_args()

    recs = json.load(open(args.dataset, encoding="utf-8"))["records"]
    years = parse_years(args.years)
    if years:
        recs = [r for r in recs if r["year"] in years]
    if not recs:
        raise SystemExit("no records match the filter")
    kk = []
    if args.kerrokantasi and os.path.exists(args.kerrokantasi):
        kk = json.load(open(args.kerrokantasi, encoding="utf-8"))["records"]
        if years:
            kk = [r for r in kk if r["year"] in years]
    ys = sorted({r["year"] for r in recs})
    span = f"{ys[0]}" if len(ys) == 1 else f"{ys[0]}–{ys[-1]}"
    build(recs, f"Kaupunkiympäristölautakunnan suunnitelmat ja kaavat {span}", args.out,
          not args.no_dedupe, args.min_sep, kk)


if __name__ == "__main__":
    main()
