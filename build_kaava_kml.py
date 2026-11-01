#!/usr/bin/env python3
"""
Render the Helsinki zoning archive (asemakaava_dataset.json from
scrape_asemakaava.py) to KML, layered by era so it stays inside Google My Maps'
limits (≤10 layers, ≤2000 features/layer).

Two views:
  --points    (default) centroid pin per plan -> one lightweight, easy-to-import
              map; each pin links the kaavakartta drawing PDF + selostus.
  --polygons  the real plan extent. Big, so pair with --split to write one file
              per era (each importable as its own My Maps layer).

    python3 build_kaava_kml.py                       # asemakaava_points.kml (9 era layers)
    python3 build_kaava_kml.py --polygons --split    # asemakaava_polygons_<era>.kml per era
"""
import json, argparse, os, html

from settings import OUT

DATASET = f"{OUT}/asemakaava_dataset.json"
OUTDIR = OUT

# era buckets (keep ≤10 so they map to ≤10 My Maps layers) + a colour each,
# dark/warm = old → light/cool = new.  KML colour is aabbggrr.
ERAS = [("–1949", lambda y: y and y < 1950,          "ff1437c6"),
        ("1950s", lambda y: y and 1950 <= y < 1960,  "ff2362e8"),
        ("1960s", lambda y: y and 1960 <= y < 1970,  "ff249ef2"),
        ("1970s", lambda y: y and 1970 <= y < 1980,  "ff36c9f4"),
        ("1980s", lambda y: y and 1980 <= y < 1990,  "ff4fd0a8"),
        ("1990s", lambda y: y and 1990 <= y < 2000,  "ff5cb85c"),
        ("2000s", lambda y: y and 2000 <= y < 2010,  "ffb8a234"),
        ("2010s", lambda y: y and 2010 <= y < 2020,  "ffc66f14"),
        ("2020s", lambda y: y and y >= 2020,         "ffc63714")]


def era_of(year):
    for name, test, _c in ERAS:
        if test(year):
            return name
    return "–1949"            # undated → oldest bucket


def desc(r):
    lines = [f'Asemakaava {html.escape(r["kaavatunnus"])}'
             + (f' — {r["kind"]}' if r["kind"] != "asemakaava" else '')]
    if r.get("hyvaksymispvm"):
        lines.append(f'Hyväksytty: {r["hyvaksymispvm"]}')
    if r.get("district"):
        lines.append(f'Kaupunginosa: {r["district"]}  ·  {int(r.get("area_m2",0)):,} m²'.replace(",", " "))
    if r.get("map_pdf"):
        lines.append(f'<a href="{r["map_pdf"]}">Kaavakartta (drawing PDF)</a>')
    elif r.get("has_map") is False:
        lines.append('<i>no digitised drawing for this plan no.</i>')
    lines.append(f'<a href="{r["selostus_pdf"]}">Kaavaselostus (report PDF)</a>')
    return "<![CDATA[" + "<br/>".join(lines) + "]]>"


def point_pm(r):
    return (f'<Placemark><styleUrl>#{era_of(r["year"])}</styleUrl>'
            f'<name>{html.escape(r["kaavatunnus"])} ({r["year"] or "?"})</name>'
            f'<description>{desc(r)}</description>'
            f'<Point><coordinates>{r["lon"]},{r["lat"]},0</coordinates></Point></Placemark>')


def _ring(coords):
    return " ".join(f'{c[0]},{c[1]},0' for c in coords)


def _depth(c):
    d = 0
    while isinstance(c, list) and c and isinstance(c[0], list):
        c = c[0]; d += 1
    return d


def poly_geom(geom):
    # normalise to a list of polygons (each = [outer_ring, hole, ...]), robust to
    # Polygon vs MultiPolygon vs a bare ring, regardless of the declared type.
    coords = geom["coordinates"]
    d = _depth(coords)
    polys = coords if d == 3 else [coords] if d == 2 else [[coords]]
    out = []
    for rings in polys:
        inner = "".join(f'<innerBoundaryIs><LinearRing><coordinates>{_ring(h)}'
                        f'</coordinates></LinearRing></innerBoundaryIs>' for h in rings[1:])
        out.append(f'<Polygon><outerBoundaryIs><LinearRing><coordinates>{_ring(rings[0])}'
                   f'</coordinates></LinearRing></outerBoundaryIs>{inner}</Polygon>')
    return out[0] if len(out) == 1 else f'<MultiGeometry>{"".join(out)}</MultiGeometry>'


def polygon_pm(r):
    return (f'<Placemark><styleUrl>#{era_of(r["year"])}</styleUrl>'
            f'<name>{html.escape(r["kaavatunnus"])} ({r["year"] or "?"})</name>'
            f'<description>{desc(r)}</description>{poly_geom(r["geometry"])}</Placemark>')


def point_style(name, color):
    return (f'<Style id="{name}"><IconStyle><color>{color}</color>'
            f'<Icon><href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href></Icon>'
            f'</IconStyle></Style>')


def polygon_style(name, color):
    fill = "7f" + color[2:]          # ~50% alpha fill
    return (f'<Style id="{name}"><LineStyle><color>{color}</color><width>1</width></LineStyle>'
            f'<PolyStyle><color>{fill}</color></PolyStyle></Style>')


def write_kml(records, title, out, polygons):
    pm = polygon_pm if polygons else point_pm
    sty = polygon_style if polygons else point_style
    styles = "".join(sty(n, c) for n, _t, c in ERAS)
    folders = ""
    for name, _t, _c in ERAS:
        recs = [r for r in records if era_of(r["year"]) == name]
        if not recs:
            continue
        recs.sort(key=lambda r: r["year"] or 0)
        folders += f'<Folder><name>{name} ({len(recs)})</name>' + "".join(pm(r) for r in recs) + '</Folder>'
    kml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           f'<name>{html.escape(title)}</name>' + styles + folders + '</Document></kml>')
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(kml)
    print(f"  {os.path.basename(out):36} {len(records):4} plans  {os.path.getsize(out)//1024} KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--polygons", action="store_true", help="real extents (default: centroid pins)")
    ap.add_argument("--split", action="store_true", help="one file per era (needed for polygons)")
    args = ap.parse_args()

    recs = json.load(open(args.dataset, encoding="utf-8"))["records"]
    ys = [r["year"] for r in recs if r["year"]]
    kindlbl = "polygons" if args.polygons else "points"
    title = f"Helsingin asemakaavat {min(ys)}–{max(ys)}"

    if args.split:
        for name, _t, _c in ERAS:
            part = [r for r in recs if era_of(r["year"]) == name]
            if part:
                write_kml(part, f"{title} ({name})",
                          f"{OUTDIR}/asemakaava_{kindlbl}_{name.strip('–') or 'pre1950'}.kml", args.polygons)
    else:
        write_kml(recs, title, f"{OUTDIR}/asemakaava_{kindlbl}.kml", args.polygons)


if __name__ == "__main__":
    main()
