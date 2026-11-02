#!/usr/bin/env python3
"""
Build a colour-coded KML (Google My Maps layers) from the plans_dataset.json
produced by scrape_decisions / scrape_decisions_2013. No network — pure render,
so you can re-slice the same dataset any number of ways without re-scraping.

    python3 -m lautakuntamuistiot.build_kml                              # all records -> one KML
    python3 -m lautakuntamuistiot.build_kml --years 2025                 # single year
    python3 -m lautakuntamuistiot.build_kml --years 2017-2026 -o all.kml # inclusive range, merged
    python3 -m lautakuntamuistiot.build_kml --years 2025 --per-year      # one KML per year in range

Each plan type is a Folder (= My Maps layer); each pin carries the heading,
decision date, the 'Päätös' / 'Esitys' summary, a link to the plan drawing (when known)
and to the decision page. Kerro kantasi consultations (scrape_consultations)
are added as one more layer, with their comment period and every drawing.

Pins never overlap: the locations are approximate (street / district level) and
many plans share one, so build() declusters at render time — any pin closer than
--min-sep metres to an already placed one is moved outward on a golden-angle
spiral around its true point until it is clear. The dataset keeps the true
coordinates; a moved pin says so in its description.
"""
import re, json, os, argparse, html, math, difflib

from .common import TYPES, PADDLE, DATASET, STAGES, plan_stage, better_decision
from .settings import OUT

KK_DATASET = f"{OUT}/kerrokantasi_dataset.json"   # scrape_consultations
ORDER = [k for k, *_ in TYPES] + ["kerrokantasi"]
ICON  = dict({k: icon for k, _l, icon, _m in TYPES}, kerrokantasi="purple-circle")
LABEL = dict({k: lbl for k, lbl, *_ in TYPES}, kerrokantasi="Kerro kantasi (consultation)")
SHORT = {"katu": "katusuunnitelma", "liikenne": "liikennesuunnitelma",
         "puisto": "puistosuunnitelma", "asemakaava": "asemakaava", "muu_k": "kaava",
         "kerrokantasi": "kerro kantasi"}
# street-level points first, so the most precise pins keep their true spot
# ("area" = centroid of a consultation's own drawn area: about as good as a place)
_PRECISION = {"manual": 0, "street": 1, "place": 2, "area": 2, "district": 3}


def parse_years(spec):
    if not spec:
        return None
    if "-" in spec:
        a, b = spec.split("-"); return set(range(int(a), int(b) + 1))
    return {int(y) for y in spec.split(",")}


def placemark(r, pos=None):
    """pos = (lon, lat) where the pin is drawn (decluster), defaults to the true point."""
    lon, lat = pos or (r["lon"], r["lat"])
    name = f'{html.escape(r["location"])} – {SHORT.get(r["plan_type"], r["plan_type"])} ' \
           f'{r["month"]:02d}/{r["year"]}'
    kk = r["plan_type"] == "kerrokantasi"
    lines = [html.escape(r["heading"]),
             f'Comment period: {r["date"]}–{r.get("close_date") or "?"}' if kk
             else f'Decision date: {r["date"]} — {STAGES[r.get("stage") or plan_stage(r)]}']
    if r.get("summary"):
        lines.append(f'<i>{html.escape(r["summary"])}</i>')
    if kk:      # consultations carry several drawings (PDFs + plan images)
        lines += [f'<a href="{u}">{html.escape(n)}</a>' for n, u in r.get("drawings", [])]
        lines.append(f'<a href="{r["decision_url"]}">Kerro kantasi page</a>')
    else:
        if r.get("map_url"):
            lines.append(f'<a href="{r["map_url"]}">Open plan drawing (PDF)</a>')
        others = [(n, u) for n, u in r.get("attachments", []) if u != r.get("map_url")]
        if others:
            lines.append("Other attachments: " + ", ".join(
                f'<a href="{u}">{html.escape(n)}</a>' for n, u in others))
        lines.append(f'<a href="{r["decision_url"]}">Decision page</a>')
    moved = _dist_m(r["lon"], r["lat"], lon, lat)
    lines.append(f'<small>Location: {html.escape(r["location"])}, approx: '
                 f'{r.get("geocode","?")}-level'
                 + (f'; pin offset {moved:.0f} m to avoid overlap' if moved >= 1 else '')
                 + '</small>')
    desc = "<![CDATA[" + "<br/>".join(lines) + "]]>"
    return (f'<Placemark><styleUrl>#{r["plan_type"]}</styleUrl>'
            f'<name>{name}</name><description>{desc}</description>'
            f'<Point><coordinates>{lon:.6f},{lat:.6f},0</coordinates></Point></Placemark>')


# ── declustering ───────────────────────────────────────────────────────────────
_M_LAT = 110_574.0                                     # metres per degree latitude


def _m_lon(lat):
    return 111_320.0 * math.cos(math.radians(lat))


def _dist_m(lon1, lat1, lon2, lat2):
    return math.hypot((lon2 - lon1) * _m_lon((lat1 + lat2) / 2), (lat2 - lat1) * _M_LAT)


def decluster(records, min_sep=40.0):
    """{id(record): (lon, lat)} with every pair >= min_sep metres apart.
    Precise pins are placed first; each later pin tries its true point, then
    successive golden-angle spiral positions (r = 0.8·min_sep·√k), and takes the
    first one that is clear. A grid hash (cell = min_sep) keeps it O(n)."""
    golden = math.pi * (3 - math.sqrt(5))
    # one planar frame for everybody (a per-pin cos(lat) scale would skew the grid)
    mx, my = _m_lon(sum(r["lat"] for r in records) / max(len(records), 1)), _M_LAT
    grid, pos = {}, {}
    order = sorted(records, key=lambda r: (_PRECISION.get(r.get("geocode"), 9),
                                           r["year"], r["month"], r["asia_id"], r["plan_type"]))
    for r in order:
        lat0, lon0 = r["lat"], r["lon"]
        k = 0
        while True:
            rad, th = 0.8 * min_sep * math.sqrt(k), k * golden
            x, y = lon0 * mx + rad * math.cos(th), lat0 * my + rad * math.sin(th)
            cx, cy = int(x // min_sep), int(y // min_sep)
            clear = all(math.hypot(x - px, y - py) >= min_sep
                        for i in (-1, 0, 1) for j in (-1, 0, 1)
                        for px, py in grid.get((cx + i, cy + j), ()))
            if clear:
                break
            k += 1
        grid.setdefault((cx, cy), []).append((x, y))
        pos[id(r)] = (x / mx, y / my)
    return pos


_better = better_decision     # which of two records of the same case to keep (common)


def _norm_title(t):
    t = re.sub(r'^(?:kaupunkisuunnittelulautakunnan|yleisten töiden lautakunnan)\s+', '', t.lower())
    return re.sub(r'\(.*?\)|[^a-zäöå0-9 ]', ' ', t).split()


def dedupe_records(records):
    """One pin per (asia_id, plan_type) — collapses a plan decided in several
    meetings/years (incl. a predecessor committee's proposal + u540's approval)
    to its best single decision. Distinct plan types for one case are kept.

    Jan–May 2017 is covered by two sources (hela bulletins + the ES index) under
    different ids; a hela record with the same committee, date and type as an ES
    record and a near-identical title is the same decision and is dropped."""
    es_by = {}
    for r in records:
        if not r["asia_id"].startswith("hela-"):
            es_by.setdefault((r["dm"], r["date"], r["plan_type"]), []).append(_norm_title(r["title"]))
    kept = []
    for r in records:
        if r["asia_id"].startswith("hela-"):
            mine = _norm_title(r["title"])
            if any(difflib.SequenceMatcher(None, mine, o).ratio() >= 0.8
                   for o in es_by.get((r["dm"], r["date"], r["plan_type"]), ())):
                continue
        kept.append(r)
    best = {}
    for r in kept:
        k = (r["asia_id"], r["plan_type"])
        if k not in best or _better(r, best[k]):
            best[k] = r
    return list(best.values())


def build(records, title, out, dedupe=True, min_sep=40.0, extra=()):
    """extra = records of other sources (Kerro kantasi) — not deduped against the
    decisions, but declustered together with them so no two pins overlap."""
    if dedupe:
        records = dedupe_records(records)
    records = list(records) + list(extra)
    pos = decluster(records, min_sep) if min_sep > 0 else {}
    bytype = {k: [] for k in ORDER}
    for r in records:
        bytype.setdefault(r["plan_type"], []).append(r)
    folders = ""
    for k in ORDER:
        recs = sorted(bytype.get(k, []), key=lambda r: (r["year"], r["month"]))
        folders += (f'<Folder><name>{LABEL[k]} ({len(recs)})</name>'
                    + "".join(placemark(r, pos.get(id(r))) for r in recs) + '</Folder>')
    styles = "".join(
        f'<Style id="{k}"><IconStyle><Icon><href>{PADDLE.format(ICON[k])}</href></Icon></IconStyle></Style>'
        for k in ORDER)
    kml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           f'<name>{html.escape(title)}</name>' + styles + folders + '</Document></kml>')
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(kml)
    n = sum(len(bytype.get(k, [])) for k in ORDER)
    print(f"  {os.path.basename(out):28} {n:4} pins  "
          + " ".join(f"{k}:{len(bytype.get(k,[]))}" for k in ORDER))
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--years", default=None, help="e.g. 2025 | 2017-2026 | 2019,2021")
    ap.add_argument("--dm", default=None, help="filter by committee id")
    ap.add_argument("--per-year", action="store_true")
    ap.add_argument("--no-dedupe", action="store_true",
                    help="keep every decision as its own pin (default: one per asia+type)")
    ap.add_argument("--min-sep", type=float, default=40.0,
                    help="minimum metres between pins; overlapping ones are spread out (0 = off)")
    ap.add_argument("--kerrokantasi", default=KK_DATASET,
                    help="Kerro kantasi consultations dataset, added as its own layer "
                         "if the file exists ('' = leave out)")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    ds = json.load(open(args.dataset, encoding="utf-8"))
    recs = ds["records"]
    years = parse_years(args.years)
    if years:
        recs = [r for r in recs if r["year"] in years]
    if args.dm:
        recs = [r for r in recs if r["dm"] == args.dm]
    if not recs:
        raise SystemExit("no records match the filter")
    kk = []
    if args.kerrokantasi and os.path.exists(args.kerrokantasi) and not args.dm:
        kk = json.load(open(args.kerrokantasi, encoding="utf-8"))["records"]
        if years:
            kk = [r for r in kk if r["year"] in years]

    outdir = OUT
    dedupe = not args.no_dedupe
    if args.per_year:
        for y in sorted({r["year"] for r in recs}):
            build([r for r in recs if r["year"] == y],
                  f"Kaupunkiympäristölautakunnan suunnitelmat ja kaavat {y}",
                  f"{outdir}/plans_{y}.kml", dedupe, args.min_sep,
                  [r for r in kk if r["year"] == y])
    else:
        ys = sorted({r["year"] for r in recs})
        span = f"{ys[0]}" if len(ys) == 1 else f"{ys[0]}–{ys[-1]}"
        out = args.out or f"{outdir}/plans_{ys[0]}_{ys[-1]}.kml"
        build(recs, f"Kaupunkiympäristölautakunnan suunnitelmat ja kaavat {span}", out, dedupe,
              args.min_sep, kk)


if __name__ == "__main__":
    main()
