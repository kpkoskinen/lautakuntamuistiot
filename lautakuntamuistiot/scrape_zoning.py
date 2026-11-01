#!/usr/bin/env python3
"""
Build the full Helsinki **zoning-plan (asemakaava) archive** dataset — the plans
whose drawings go back to the 1830s, long before the 2017 decision records.

Source (open, no key): Helsinki's WFS plan index + the ptp.hel.fi document service.
  - index:  https://kartta.hel.fi/ws/geoserver/avoindata/wfs
            layer avoindata:Kaavahakemisto_alue_kaava_voimassa  (valid plans)
                  + ...maanalainenkaava_voimassa                (underground)
            each feature: kaavatunnus (plan no.), dates, district, polygon geom
  - drawing: https://ptp.hel.fi/DataHandlers/kaavapdf/?id=<kaavatunnus>
  - report:  https://ptp.hel.fi/DataHandlers/kaavaselostuspdf/?id=<kaavatunnus>

Unlike the decision scraper this gives the real plan **extent** (polygon) and
near-complete drawing coverage across ~130 years. Writes asemakaava_dataset.json
(records with geometry + centroid + verified PDF links); build_zoning_kml renders it.

  python3 -m lautakuntamuistiot.scrape_zoning              # pull + verify drawing links
  python3 -m lautakuntamuistiot.scrape_zoning --no-verify  # pull only (fast), link optimistically

GOTCHA baked in: the ptp handler returns HTTP 200 + a 780-byte PNG placeholder
when a plan has no PDF, so we verify by magic bytes (%PDF), never status code.
"""
import urllib.request, json, argparse, os, time

from .settings import OUT, USER_AGENT

WFS = ("https://kartta.hel.fi/ws/geoserver/avoindata/wfs?service=WFS&version=2.0.0"
       "&request=GetFeature&typeNames=avoindata:{layer}&outputFormat=application/json"
       "&srsName=EPSG:4326&count=20000")
PDF_MAP = "https://ptp.hel.fi/DataHandlers/kaavapdf/?id={}"
PDF_SEL = "https://ptp.hel.fi/DataHandlers/kaavaselostuspdf/?id={}"
UA = {"User-Agent": USER_AGENT}
LAYERS = [("Kaavahakemisto_alue_kaava_voimassa", "asemakaava"),
          ("Kaavahakemisto_alue_maanalainenkaava_voimassa", "maanalainen")]
DATASET = f"{OUT}/asemakaava_dataset.json"


def fetch_layer(layer):
    with urllib.request.urlopen(urllib.request.Request(WFS.format(layer=layer), headers=UA), timeout=90) as r:
        return json.load(r)["features"]


def bbox_centroid(geom):
    """bbox + centre over all rings of a (Multi)Polygon, coords already lon,lat."""
    xs, ys = [], []
    def walk(c):
        if c and isinstance(c[0], (int, float)):
            xs.append(c[0]); ys.append(c[1])
        else:
            for x in c:
                walk(x)
    walk(geom["coordinates"])
    return [round((min(xs)+max(xs))/2, 6), round((min(ys)+max(ys))/2, 6)], \
           [round(min(xs), 6), round(min(ys), 6), round(max(xs), 6), round(max(ys), 6)]


def round_geom(geom):
    def r(c):
        if c and isinstance(c[0], (int, float)):
            return [round(c[0], 6), round(c[1], 6)]
        return [r(x) for x in c]
    return {"type": geom["type"], "coordinates": r(geom["coordinates"])}


def is_pdf(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            return r.read(4) == b"%PDF"
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-verify", action="store_true", help="skip per-plan PDF magic-byte check")
    ap.add_argument("--dataset", default=DATASET)
    args = ap.parse_args()

    records = []
    for layer, kind in LAYERS:
        feats = fetch_layer(layer)
        print(f"{layer}: {len(feats)} features")
        for f in feats:
            p = f["properties"]
            g = f.get("geometry")
            if not g:
                continue
            tunnus = str(p.get("kaavatunnus") or "").strip()
            if not tunnus:
                continue
            centroid, bbox = bbox_centroid(g)
            hyv = p.get("hyvaksymispvm") or ""
            year = int(hyv[-4:]) if hyv[-4:].isdigit() else None
            records.append(dict(
                kaavatunnus=tunnus, kind=kind, luokka=p.get("luokka"),
                hyvaksymispvm=hyv, lainvoimaisuuspvm=p.get("lainvoimaisuuspvm"),
                year=year, district=p.get("sijaintialue"),
                area_m2=round(p.get("pintaala") or 0, 1),
                lon=centroid[0], lat=centroid[1], bbox=bbox,
                map_pdf=PDF_MAP.format(tunnus), selostus_pdf=PDF_SEL.format(tunnus),
                has_map=None, has_selostus=None,
                geometry=round_geom(g)))

    # dedupe by kaavatunnus (a plan can span >1 index polygon)
    seen = {}
    for r in records:
        seen.setdefault(r["kaavatunnus"], r)
    records = list(seen.values())
    print(f"{len(records)} unique plans")

    if not args.no_verify:
        print("verifying drawing PDFs (magic bytes; ptp returns 200+PNG when missing) ...")
        for i, r in enumerate(records, 1):
            r["has_map"] = is_pdf(r["map_pdf"])
            if not r["has_map"]:
                r["map_pdf"] = None
            if i % 250 == 0:
                print(f"  {i}/{len(records)}  ({sum(1 for x in records[:i] if x['has_map'])} with drawing)")
            time.sleep(0.03)

    ds = {"generated": time.strftime("%Y-%m-%d"),
          "source": "Helsinki WFS Kaavahakemisto + ptp.hel.fi kaavapdf",
          "note": "Valid Helsinki zoning plans (asemakaava) with polygon geometry and "
                  "drawing-PDF links. map_pdf null = no digitised drawing for that plan no.",
          "records": records}
    os.makedirs(os.path.dirname(args.dataset) or ".", exist_ok=True)
    json.dump(ds, open(args.dataset, "w", encoding="utf-8"), ensure_ascii=False)
    withmap = sum(1 for r in records if r["has_map"]) if not args.no_verify else "unverified"
    yrs = [r["year"] for r in records if r["year"]]
    print(f"\nwrote {len(records)} plans ({withmap} with drawing), years {min(yrs)}–{max(yrs)}")
    print(f"  -> {args.dataset}")


if __name__ == "__main__":
    main()
