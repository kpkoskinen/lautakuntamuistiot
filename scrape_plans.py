#!/usr/bin/env python3
"""
Scrape a committee's plan decisions into a reusable JSON dataset — the single
intermediate that every map is then built from (build_kml.py), so you never have
to re-scrape to re-render.

For each plan decision it records a normalised dict:

    committee, dm, asia_id, plan_type (+label), heading (the decision page <h1>),
    title (agenda line), summary (the "Päätös" decision text), date/year/month,
    location, lat, lon, geocode (confidence/source), decision_url, map_url (the
    plan-DRAWING pdf or null).

Records are upserted into the dataset keyed on (dm, asia_id, plan_type), so
re-running a year refreshes it in place. Geocoding goes through a persistent
cache file, so coordinates are reproducible and any manual fixes stay put.

    python3 scrape_plans.py --year 2025                 # u540, append to dataset
    python3 scrape_plans.py --year 2024 --dm u540
    # then:  python3 build_kml.py ...

Only u540 (Kaupunkiympäristölautakunta, 2017→) has a server-rendered meeting
index that this can enumerate. Pre-2017 predecessor committees
(Kaupunkisuunnittelulautakunta, Yleisten töiden lautakunta) exist on
paatokset.hel.fi but their meeting lists are JS-only — see README.
"""
import re, json, os, argparse, html, time

from list_meetings import list_meetings
from build_year_map import fetch, MONTHS
from make_street_plans_map import geocode
from settings import OUT
from build_plans_map import (TYPES, classify, extract_pdf, loc_from_text,
                             EXCLUDE, decision_page)

DATASET = f"{OUT}/plans_dataset.json"
GCACHE  = f"{OUT}/geocode_cache.json"
LABEL   = {k: lbl for k, lbl, *_ in TYPES}
COMMITTEE = {"u540": "Kaupunkiympäristölautakunta"}

# ── decision-page field extraction (shared with bootstrap_dataset.py) ──────────
_STOP = re.compile(r'Avaa kaikki|Päätösehdotus|Käsittely|Esittelijä|Esittelij|'
                   r'Päätöshistoria|Muutoksenhaku|Lisätiedot|Tämä päätös')

def decision_fields(page):
    """(heading, summary, map_url) from a decision-page HTML.
    heading = the <h1> (richer than the agenda line: has district + plan number);
    summary = the committee's actual 'Päätös' text, trimmed; map_url = plan drawing."""
    heading = None
    m = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
    if m:
        heading = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', m.group(1)))).strip() or None
    summary = None
    txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', page)))
    s = re.search(r'\bPäätös\b\s+(.{25,}?)(?:' + _STOP.pattern + ')', txt)
    if s:
        summary = s.group(1).strip()
        if len(summary) > 320:
            summary = summary[:317].rsplit(' ', 1)[0] + '…'
    return heading, summary, extract_pdf(page)


# ── geocode cache ──────────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default

def cached_geocode(loc, cache):
    if loc in cache:
        return cache[loc]
    lat, lon, conf = geocode(loc, loc)
    cache[loc] = [lat, lon, conf]
    return cache[loc]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dm", default="u540")
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--nmax", type=int, default=45)
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--cache", default=GCACHE)
    args = ap.parse_args()

    committee = COMMITTEE.get(args.dm, args.dm)
    ds = load_json(args.dataset, {"generated": None, "records": []})
    cache = load_json(args.cache, {})
    # index existing records for upsert
    bykey = {(r["dm"], r["asia_id"], r["plan_type"]): i for i, r in enumerate(ds["records"])}

    print(f"[1/3] listing {args.dm} meetings for {args.year} ...")
    meetings = list_meetings(args.dm, args.year, args.nmax, verbose=False)
    print(f"      {len(meetings)} meetings")

    print("[2/3] scraping agendas + classifying ...")
    seen, items = set(), []
    for mtg in meetings:
        h = fetch(mtg["url"])
        _, mo, y = mtg["date"].split(".")
        for m in re.finditer(r'<a[^>]+href="(/fi/asia/hel-[0-9-]+[^"]*)"[^>]*>(.*?)</a>', h, re.S):
            txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(2))).strip()
            if "§" not in txt or EXCLUDE.search(txt):
                continue
            key = classify(txt.lower())
            if not key:
                continue
            asia = re.search(r'hel-\d{4}-\d+', m.group(1)).group(0)
            if (key, asia) in seen:
                continue
            seen.add((key, asia))
            items.append(dict(plan_type=key, asia_id=asia,
                              title=re.sub(r'^\s*\d+\.\s*/\s*\d+\s*§\s*', '', txt),
                              decision_url="https://paatokset.hel.fi" + m.group(1),
                              month=int(mo), year=int(y), date=mtg["date"]))
    print(f"      {len(items)} plan items")

    print("[3/3] decision page -> heading + summary + drawing + geocode ...")
    added = updated = skipped = 0
    for it in items:
        page = decision_page(it["decision_url"])
        heading, summary, map_url = decision_fields(page)
        loc = loc_from_text(it["title"]) or loc_from_text(re.sub(r'<[^>]+>', ' ', page[:9000]))
        if not loc:
            skipped += 1; continue
        lat, lon, conf = cached_geocode(loc, cache)
        if lat is None:
            skipped += 1; continue
        rec = dict(committee=committee, dm=args.dm, asia_id=it["asia_id"],
                   plan_type=it["plan_type"], plan_type_label=LABEL[it["plan_type"]],
                   heading=heading or it["title"], title=it["title"], summary=summary,
                   date=it["date"], year=it["year"], month=it["month"],
                   location=loc, lat=lat, lon=lon, geocode=conf,
                   decision_url=it["decision_url"], map_url=map_url)
        k = (args.dm, it["asia_id"], it["plan_type"])
        if k in bykey:
            ds["records"][bykey[k]] = rec; updated += 1
        else:
            bykey[k] = len(ds["records"]); ds["records"].append(rec); added += 1

    ds["generated"] = time.strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(args.dataset) or ".", exist_ok=True)
    json.dump(ds, open(args.dataset, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(cache, open(args.cache, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    withdraw = sum(1 for r in ds["records"] if r["map_url"])
    print(f"\n{args.year}: +{added} new, {updated} updated, {skipped} skipped")
    print(f"dataset now {len(ds['records'])} records ({withdraw} with drawing) -> {args.dataset}")


if __name__ == "__main__":
    main()
