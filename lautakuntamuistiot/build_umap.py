#!/usr/bin/env python3
"""
Build a uMap (umap.openstreetmap.fr) map file from the same datasets as build_kml.
No network — pure render.

    python3 -m lautakuntamuistiot.build_umap                       # all records -> helsinki_plans.umap
    python3 -m lautakuntamuistiot.build_umap --years 2020-2026 -o recent.umap
    python3 -m lautakuntamuistiot.build_umap --remote-base URL   # layers load from URL/<type>.geojson
    python3 -m lautakuntamuistiot.build_umap --combined [--remote-base URL]   # one clustered layer
    python3 -m lautakuntamuistiot.build_umap --cluster-per-type [--remote-base URL]   # six

The output is uMap's own export format (.umap: GeoJSON layers plus the map's
settings), so one import gives the whole map: one coloured layer per plan type
plus the Kerro kantasi layer, popups, a stage and year filter, centre and licence.
uMap imports KML too, but only as data, without these settings.

Each pin's popup is its `description`, written in uMap's own markup (**bold**,
*italic*, [[url|text]] links). The facts are also plain properties (date, year,
stage, plan_type, location, drawing_url, decision_url, ...), so they show in
uMap's table view and can be used in filters or a custom popup template.

Each layer is also written as plain GeoJSON to a `umap/` folder next to the
output (katu.geojson, liikenne.geojson, ...). A uMap layer can load such a file from
a URL every time the map opens (layer settings -> Remote data), so a map that points
at the files in a git repository shows whatever was last committed. --remote-base
writes a .umap whose layers already point there: URL/<type>.geojson, no data inside.

The background is Jawg Light, a grey OpenStreetMap map that uMap offers, so the
coloured pins stand out.

Pins are deduped and declustered exactly as in build_kml.

Combined, clustered map (--combined): all plan types in ONE layer of uMap's "Clustered"
type, so pins of different types that overlap merge into one count circle; clicking it
zooms in, and pins at the same spot fan out to choose from. Each pin keeps its plan
type's colour (per-pin `_umap_options.color`), and the layer toggles become a "Plan
type" filter. Hovering a pin shows its date, heading and the start of the summary
(the `hover` property). Pins stay at their true points (no declustering): the clustering handles
the overlaps. Its data is umap/all.geojson, which every build writes next to the
per-type files, so the daily job keeps it current without extra options.
"""
import argparse, json, os

from .build_kml import (KK_DATASET, LABEL, ORDER, SHORT, _dist_m, decluster,
                        dedupe_records, parse_years)
from .common import DATASET, STAGES, plan_stage
from .settings import OUT

# the KML paddle colours, as uMap colours
COLOR = {"katu": "#d7301f", "liikenne": "#2b6cd6", "puisto": "#1a9850",
         "asemakaava": "#e6b400", "muu_k": "#e7298a", "kerrokantasi": "#7b3fbf"}
# grey background, as listed by umap.openstreetmap.fr (its Positron entry needs a CARTO key)
TILELAYER = {"name": "Jawg Light", "minZoom": 0, "maxZoom": 18, "tms": False,
             "url_template": "https://tile.jawg.io/jawg-light/{z}/{x}/{y}.png?api-key=community",
             "attribution": "Tiles courtesy of [[https://www.jawg.io/|jawgmaps]] - Map data "
                            "[[http://osm.org/copyright/|&copy; OpenStreetMap contributors]], "
                            "under ODbL."}
CLUSTER_COLOR = "#4a4a4a"                                 # count circles of the combined layer
CLUSTER_RADIUS = 60                                      # px; uMap's default is 80
CENTER = [24.94, 60.19]                                  # lon, lat — Helsinki
ATTRIBUTION = ("Decisions: City of Helsinki (paatokset.hel.fi), Kerro kantasi; "
               "locations geocoded with Nominatim, © OpenStreetMap contributors (ODbL). "
               "Experimental, heuristically extracted: pins are approximate.")


def _text(s):
    """Plain text for uMap markup: no accidental bold/italic, links or templates."""
    return (s or "").replace("*", "∗").replace("[[", "[ [").replace("{", "(").replace("}", ")")


HOVER_CHARS = 140                                        # summary characters in the hover text


def hover_text(r):
    """Plain-text hover label: date, heading and the start of the summary."""
    text = f'{r["date"]} · {r["heading"]}'
    summary = (r.get("summary") or "").strip()
    if summary:
        cut = summary if len(summary) <= HOVER_CHARS else \
            summary[:HOVER_CHARS].rsplit(" ", 1)[0] + "…"
        text += f" — {cut}"
    return text


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
    props["plan_type_label"] = LABEL[r["plan_type"]]
    props["hover"] = hover_text(r)
    return {"type": "Feature", "properties": props,
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]}}


def combined_features(records):
    """Every pin at its true point, coloured by plan type, for the clustered layer."""
    out = []
    for k in ORDER:
        for r in sorted((r for r in records if r["plan_type"] == k),
                        key=lambda r: (r["year"], r["month"])):
            f = feature(r)
            f["properties"]["_umap_options"] = {"color": COLOR[k]}
            out.append(f)
    return out


def build(records, title, out, dedupe=True, min_sep=40.0, extra=(), remote_base=None,
          combined=False, cluster_per_type=False):
    if dedupe:
        records = dedupe_records(records)
    records = list(records) + list(extra)
    pos = decluster(records, min_sep) if min_sep > 0 and not combined else {}
    bytype = {k: [] for k in ORDER}
    for r in records:
        bytype.setdefault(r["plan_type"], []).append(r)
    layers_dir = os.path.join(os.path.dirname(out) or ".", "umap")
    os.makedirs(layers_dir, exist_ok=True)
    layers = []
    for k in ORDER:
        recs = sorted(bytype.get(k, []), key=lambda r: (r["year"], r["month"]))
        features = [feature(r, pos.get(id(r))) for r in recs]
        with open(os.path.join(layers_dir, f"{k}.geojson"), "w", encoding="utf-8") as f:
            json.dump({"type": "FeatureCollection", "features": features}, f,
                      ensure_ascii=False, separators=(",", ":"))
        props = {"name": f"{LABEL[k]} ({len(recs)})", "color": COLOR[k],
                 "iconClass": "Circle", "displayOnLoad": True,
                 "browsable": True, "inCaption": True}
        if cluster_per_type:                     # count circles in the layer's colour
            props.update({"type": "Cluster", "cluster": {"radius": CLUSTER_RADIUS},
                          "showLabel": None, "labelKey": "hover"})
        if remote_base:                          # counts would go stale: leave them out
            props["name"] = LABEL[k]
            props["remoteData"] = {"url": f"{remote_base.rstrip('/')}/{k}.geojson",
                                   "format": "geojson"}
            features = []
        layers.append({"type": "FeatureCollection", "features": features,
                       "properties": props})
    allf = combined_features(records)
    with open(os.path.join(layers_dir, "all.geojson"), "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": allf}, f,
                  ensure_ascii=False, separators=(",", ":"))
    fields = [{"key": "name", "type": "String"}, {"key": "description", "type": "Text"},
              {"key": "stage", "type": "String"}, {"key": "year", "type": "Number"}]
    filters = [{"fieldKey": "stage", "widget": "Checkbox", "label": "Stage"},
               {"fieldKey": "year", "widget": "MinMax", "label": "Year"}]
    if combined:
        props = {"name": "Plans and consultations", "color": CLUSTER_COLOR,
                 "type": "Cluster", "cluster": {"radius": CLUSTER_RADIUS},
                 "showLabel": None, "labelKey": "hover",          # label on hover
                 "iconClass": "Circle", "displayOnLoad": True,
                 "browsable": True, "inCaption": True}
        if remote_base:
            props["remoteData"] = {"url": f"{remote_base.rstrip('/')}/all.geojson",
                                   "format": "geojson"}
            allf = []
        layers = [{"type": "FeatureCollection", "features": allf, "properties": props}]
        fields.insert(2, {"key": "plan_type_label", "type": "String"})
        filters.insert(0, {"fieldKey": "plan_type_label", "widget": "Checkbox",
                           "label": "Plan type"})
    doc = {
        "type": "umap",
        "properties": {
            "name": title,
            "description": ("Helsinki committee plan decisions and Kerro kantasi consultations, "
                            + ("coloured by plan type. Numbers are groups of pins: click to "
                               "zoom in; where several plans share one spot, click the number "
                               "again to fan them out, then click the pins one by one (close a "
                               "popup with ×; a click on the map closes the fan). Hover a pin "
                               "for a preview. " if combined else
                               "one clustered layer per plan type: numbers are groups of pins of "
                               "that type, click to zoom in. Pins that would overlap are spread "
                               "at least 40 m apart. Hover a pin for a preview. "
                               if cluster_per_type else "one layer per plan type. ")
                            + ATTRIBUTION),
            "shortCredit": "Data: City of Helsinki, © OpenStreetMap contributors (ODbL)",
            "zoom": 12, "popupShape": "Large", "tilelayer": TILELAYER,
            "fields": fields,
            "filters": filters,
            "onLoadPanel": "caption",
        },
        "geometry": {"type": "Point", "coordinates": CENTER},
        "layers": layers,
    }
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    n = sum(len(bytype.get(k, [])) for k in ORDER)
    print(f"  {os.path.basename(out):28} {n:4} pins  (+ {layers_dir}/*.geojson)  "
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
    ap.add_argument("--remote-base", default=None,
                    help="URL of a folder holding the umap/*.geojson files; the layers load "
                         "from there instead of carrying the data, e.g. https://raw."
                         "githubusercontent.com/OWNER/REPO/main/data/umap")
    ap.add_argument("--combined", action="store_true",
                    help="one clustered layer with every plan type (umap/all.geojson), pins at "
                         "their true points, plan type as a filter")
    ap.add_argument("--cluster-per-type", action="store_true",
                    help="one clustered layer per plan type, pins spread --min-sep apart")
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
          not args.no_dedupe, args.min_sep, kk, args.remote_base, args.combined,
          args.cluster_per_type)


if __name__ == "__main__":
    main()
