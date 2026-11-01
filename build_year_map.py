#!/usr/bin/env python3
"""
Step 2: build the full-year street-plan KML from committee meetings — no API.

Walks every Kaupunkiympäristölautakunta meeting of a year (via list_meetings),
scrapes each server-rendered agenda for `katusuunnitelma` decisions, geocodes them
(street -> district, tiered), and writes a RED-pin KML with the month + year in each
caption. Output goes to output/ (never committed).

    python3 build_year_map.py --year 2025
    python3 build_year_map.py --year 2025 -o out.kml
"""
import urllib.request, re, argparse, os, html
from list_meetings import list_meetings
from make_street_plans_map import geocode, UA, RED_ICON
from settings import OUT

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

STREET_RE = re.compile(
    r'[A-ZÄÖÅ][\wäöåÄÖÅ-]*(?:katu|tie|ranta|kuja|laituri|väylä|aukio|polku|kaari|rinne|tori|silta|penger)')


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception:
        return ""


def parse_title(title):
    """'6. / 487 § Siltasaarenkatu, Hämeentie, katusuunnitelma, Kallio' ->
       ('Siltasaarenkatu', 'Kallio', cleaned title)."""
    t = re.sub(r'^\s*\d+\.\s*/\s*\d+\s*§\s*', '', title).strip()
    streets = STREET_RE.findall(t)
    street = streets[0] if streets else t.split(',')[0].split()[0]
    district = ""
    m = re.search(r'katusuunnitelma[t]?\s*,?\s*(.+)$', t, re.I)
    if m:
        toks = [re.sub(r'\s*nro.*$', '', x, flags=re.I).strip() for x in m.group(1).split(',')]
        toks = [x for x in toks if x and not re.match(r'^\d', x)]
        if toks:
            district = toks[-1]
    return street, district, t


def extract_decisions(meeting):
    h = fetch(meeting["url"])
    _, mo, y = meeting["date"].split(".")
    found = []
    for m in re.finditer(r'<a[^>]+href="(/fi/asia/hel-[0-9-]+[^"]*)"[^>]*>(.*?)</a>', h, re.S):
        txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(2))).strip()
        if 'katusuunnitelma' not in txt.lower():
            continue
        street, district, full = parse_title(txt)
        asia = re.search(r'hel-\d{4}-\d+', m.group(1)).group(0)
        found.append(dict(street=street, district=district, title=full,
                          decision="https://paatokset.hel.fi" + m.group(1),
                          month=int(mo), year=int(y), date=meeting["date"], asia=asia))
    return found


def placemark(d, lat, lon, conf):
    cap = f'{html.escape(d["street"])} ({MONTHS[d["month"]]} {d["year"]})'
    desc = ("<![CDATA["
            f'{html.escape(d["title"])}<br/>'
            f'Decision date: {d["date"]}<br/>'
            f'<a href="{d["decision"]}">Decision page (plan PDFs here)</a><br/>'
            f'<i>approx location: {conf}-level</i>'
            "]]>")
    return (f'<Placemark><styleUrl>#rw</styleUrl>'
            f'<name>{cap}</name><description>{desc}</description>'
            f'<Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dm", default="u540")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--nmax", type=int, default=45)
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()
    out = args.out or f"{OUT}/street_plans_{args.year}.kml"

    print(f"[1/3] listing {args.dm} meetings for {args.year} ...")
    meetings = list_meetings(args.dm, args.year, args.nmax, verbose=False)
    print(f"      {len(meetings)} meetings")

    print(f"[2/3] scraping agendas for katusuunnitelma decisions ...")
    seen, decisions = set(), []
    for mtg in meetings:
        for d in extract_decisions(mtg):
            if d["asia"] in seen:
                continue
            seen.add(d["asia"])
            decisions.append(d)
    print(f"      {len(decisions)} katusuunnitelma decisions found")

    print(f"[3/3] geocoding + building KML ...")
    cache, pins, skipped = {}, [], []
    for d in decisions:
        key = (d["street"], d["district"])
        if key not in cache:
            cache[key] = geocode(d["street"], d["district"])   # rate-limited inside
        lat, lon, conf = cache[key]
        if lat is None:
            skipped.append(f'{d["street"]} ({d["date"]})')
            continue
        pins.append(placemark(d, lat, lon, conf))
        print(f'  {d["street"]:22} {MONTHS[d["month"]]} {d["year"]}  -> {lat:.4f},{lon:.4f} ({conf})')

    style = (f'<Style id="rw"><IconStyle><color>ff0000ff</color>'
             f'<Icon><href>{RED_ICON}</href></Icon></IconStyle></Style>')
    kml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           f'<name>Helsinki street plans {args.year}</name>'
           + style + "".join(pins) + '</Document></kml>')
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(kml)
    print(f"\nwrote {len(pins)} RED pins -> {out}")
    if skipped:
        print(f"  could not geocode ({len(skipped)}):", skipped)


if __name__ == "__main__":
    main()
