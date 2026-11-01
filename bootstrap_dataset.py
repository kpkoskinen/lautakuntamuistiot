#!/usr/bin/env python3
"""
One-off migration: build plans_dataset.json from the already-validated per-year
KMLs (plans_YYYY.kml), then enrich each record with the decision-page <h1>
heading and the 'Päätös' summary.

Why bootstrap from the KMLs instead of re-scraping: the KMLs carry hand-verified
coordinates (out-of-area and playground fixes, admin-item removals) and live
geocoding is non-deterministic — re-scraping would wobble them. So we take
coords/links/type/date straight from the KMLs and only FETCH the two new text
fields. Kept for reference only: the scrape_plans_*.py scrapers maintain the
dataset now and build_kml.py renders from it.

It OVERWRITES plans_dataset.json and geocode_cache.json, so it refuses to run
over an existing dataset (or with no per-year KMLs to read) unless --force.

    python3 bootstrap_dataset.py --force    # reads plans_2017.kml .. plans_2026.kml
"""
import re, json, os, glob, html, time, argparse

from settings import OUT

from build_year_map import MONTHS
from scrape_plans import decision_fields, DATASET, GCACHE
from build_plans_map import decision_page   # fetch-once cache

MON = {m: i for i, m in enumerate(MONTHS)}
DIR = OUT
COMMITTEE, DM = "Kaupunkiympäristölautakunta", "u540"


def parse_kml(path):
    h = open(path, encoding="utf-8").read()
    out = []
    for pm in re.finditer(r'<Placemark>(.*?)</Placemark>', h, re.S):
        b = pm.group(1)
        key = re.search(r'<styleUrl>#([^<]+)</styleUrl>', b)
        name = re.search(r'<name>(.*?)</name>', b, re.S)
        cd = re.search(r'<!\[CDATA\[(.*?)\]\]>', b, re.S)
        coord = re.search(r'<coordinates>([-\d.]+),([-\d.]+)', b)
        if not (key and name and cd and coord):
            continue
        nm = re.match(r'^(.*)\s\((\w{3})\s(\d{4})\)\s*$', html.unescape(name.group(1)), re.S)
        if not nm:
            continue
        loc, mon, year = nm.group(1), MON.get(nm.group(2), 0), int(nm.group(3))
        body = cd.group(1)
        title = html.unescape(body.split("<br/>")[0]).strip()
        dec = re.search(r'href="(https://paatokset\.hel\.fi/fi/asia/[^"]+)"', body)
        mapu = re.search(r'href="(https://ahjojulkaisu\.hel\.fi/[^"]+)"[^>]*>Open plan drawing', body)
        date = re.search(r'Decision date:\s*([\d.]+)', body)
        conf = re.search(r'approx:\s*(\w+)-level', body)
        if not dec:
            continue
        asia = re.search(r'hel-\d{4}-\d+', dec.group(1))
        out.append(dict(committee=COMMITTEE, dm=DM,
                        asia_id=asia.group(0) if asia else dec.group(1),
                        plan_type=key.group(1), title=title,
                        date=date.group(1) if date else f"??.{mon:02d}.{year}",
                        year=year, month=mon, location=html.unescape(loc),
                        lon=float(coord.group(1)), lat=float(coord.group(2)),
                        geocode=conf.group(1) if conf else "kml",
                        decision_url=dec.group(1),
                        map_url=mapu.group(1) if mapu else None))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing plans_dataset.json + geocode_cache.json")
    args = ap.parse_args()
    from build_plans_map import TYPES
    LABEL = {k: lbl for k, lbl, *_ in TYPES}
    files = sorted(f for f in glob.glob(f"{DIR}/plans_*.kml")
                   if re.search(r'plans_\d{4}\.kml$', f))
    if not files:
        raise SystemExit(f"no per-year plans_YYYY.kml in {DIR} — nothing to bootstrap from")
    if os.path.exists(DATASET) and not args.force:
        raise SystemExit(f"{DATASET} exists and would be overwritten (with the geocode "
                         f"cache); pass --force if you really mean it")
    print(f"reading {len(files)} per-year KMLs ...")
    records = []
    for f in files:
        recs = parse_kml(f)
        print(f"  {os.path.basename(f):20} {len(recs)} pins")
        records.extend(recs)

    print(f"\nenriching {len(records)} records with heading + summary "
          f"({len({r['decision_url'] for r in records})} unique decision pages) ...")
    n = 0
    for r in records:
        page = decision_page(r["decision_url"])          # cached per URL
        heading, summary, _map = decision_fields(page) if page else (None, None, None)
        r["plan_type_label"] = LABEL.get(r["plan_type"], r["plan_type"])
        r["heading"] = heading or r["title"]
        r["summary"] = summary
        n += 1
        if n % 100 == 0:
            print(f"    {n}/{len(records)}")
        time.sleep(0.15)

    # order fields nicely
    cols = ["committee", "dm", "asia_id", "plan_type", "plan_type_label", "heading",
            "title", "summary", "date", "year", "month", "location", "lat", "lon",
            "geocode", "decision_url", "map_url"]
    records = [{c: r.get(c) for c in cols} for r in records]
    ds = {"generated": time.strftime("%Y-%m-%d"),
          "source": "paatokset.hel.fi — Kaupunkiympäristölautakunta (u540)",
          "records": records}
    os.makedirs(DIR, exist_ok=True)
    json.dump(ds, open(DATASET, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # seed geocode cache from the validated coords (preserves manual fixes)
    cache = {}
    for r in records:
        cache[r["location"]] = [r["lat"], r["lon"], r["geocode"]]
    json.dump(cache, open(GCACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    withmap = sum(1 for r in records if r["map_url"])
    withsum = sum(1 for r in records if r["summary"])
    print(f"\nwrote {len(records)} records ({withmap} with drawing, {withsum} with summary)")
    print(f"  -> {DATASET}")
    print(f"  -> {GCACHE}  ({len(cache)} locations)")


if __name__ == "__main__":
    main()
