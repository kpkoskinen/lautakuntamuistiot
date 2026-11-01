#!/usr/bin/env python3
"""
Build a multi-layer plans KML from a committee's meetings for a full year — no API.

Walks every Kaupunkiympäristölautakunta meeting of the year, scrapes each agenda,
classifies every plan item by type, then for each item opens its decision page to
grab (a) the plan-drawing PDF link and (b) a geocodable street/area (fallback when
the agenda title has none). Writes ONE KML with a colour-coded Folder (= Google My
Maps layer) per type; each pin has month+year in its name and a direct PDF link.

Administrative committee items (statements/appeals/budget/action-plans/land-use
agreements) are filtered out — they falsely match `suunnitelma`/`kaava` but are not
plans and have no location.

Output goes to output/ (see settings.py).  python3 build_plans_map.py --year 2025
"""
import re, argparse, os, html
from list_meetings import list_meetings
from make_street_plans_map import geocode, UA           # geocode is rate-limited
from build_year_map import fetch, STREET_RE, MONTHS
from settings import OUT

PADDLE = "http://maps.google.com/mapfiles/kml/paddle/{}.png"

TYPES = [   # (key, folder label, paddle-icon, matcher over lowercased title)
    # stems, not nominatives: titles are inflected ("katusuunnitelmien hyväksyminen",
    # "liikennesuunnitelmasta") and the nominative-only match silently dropped them.
    ("katu",      "Katusuunnitelma (street)",      "red-circle",
     lambda t: "katusuunnitelm" in t and "katu- ja puisto" not in t),
    ("liikenne",  "Liikennesuunnitelma (traffic)", "blu-circle",
     lambda t: "liikennesuunnitelm" in t),
    ("puisto",    "Puistosuunnitelma (park)",      "grn-circle",
     lambda t: "puistosuunnitelm" in t or "katu- ja puisto" in t),
    ("asemakaava","Asemakaava (zoning)",           "ylw-circle",
     lambda t: "asemakaav" in t),
    ("muu_k",     "Muu kaava",                     "pink-circle",
     lambda t: re.search(r'\w*kaava', t) is not None),
]

PLAN_WORD = re.compile(r'suunnitelma|kaava|periaat|muutos|asemakaav', re.I)
# tokens that are never a place (committee name, admin words)
ADMIN = re.compile(r'lautakun|kaupunkiympärist|oikaisu|talousarvi|maankäyttösopim|'
                   r'toimial|määrärah|hankinta|vuokra|valtuu|aloite|kokous|lausunt|'
                   r'esitys|toimintasuunnitelma|hallitukse|virastopääll|'
                   r'leikkipuisto|leikkialue|liikuntapuisto', re.I)   # generic facility words
# whole-item hard exclude: clearly not a spatial plan (statements/reports/admin)
EXCLUDE = re.compile(r'oikaisuvaatimu|talousarvi|toimintasuunnitelma|maankäyttösopim|'
                     r'määrärah|virastopääll|hankinta|vuokra|kokousaj|'
                     r'lausunto|arviointi ja seuranta|seurantaraport|karvi|'
                     r'vastaus|kuntalaisaloit|aloitteeseen|tonttivaraus|tontinvaraus|varauksen jatka', re.I)

_pages = {}                     # decision-url -> html (fetched once)


def decision_page(url):
    # keep the ?paatos= query — the drawing attachment lives under the specific
    # decision; the asia base page often shows only the print-out.
    if url not in _pages:
        _pages[url] = fetch(url)
    return _pages[url]


def classify(title_lc):
    for key, _label, _icon, match in TYPES:
        if match(title_lc):
            return key
    return None


def loc_from_text(text):
    """First geocodable street (else capitalised area token), skipping admin/plan words."""
    for s in STREET_RE.findall(text):
        if not ADMIN.search(s):
            return s
    for chunk in re.split(r'[,/]', text):
        w = chunk.strip().split(" ")[0] if chunk.strip() else ""
        if re.match(r'^[A-ZÄÖÅ]', w) and not PLAN_WORD.search(w) and not ADMIN.search(w):
            return w
    return None


def extract_pdf(page):
    """The plan-DRAWING PDF (suunnitelmapiirustus / kaavakartta / kartta) — never the
    print-out, minutes, selostus, NOR a LOCATION MAP (sijaintikartta / ilmakuva /
    havainnekuva / yleiskartta). Returns None if no real drawing is in the served HTML
    (JS-loaded for some decisions); the pin then links the decision page, not a wrong PDF."""
    anchors = [(re.sub(r'<[^>]+>', ' ', m.group(2)).lower(), m.group(1))
               for m in re.finditer(
                   r'<a[^>]+href="(https://ahjojulkaisu\.hel\.fi/[A-F0-9-]+\.pdf)"[^>]*>(.*?)</a>',
                   page, re.S)]
    anchors = [(t, u) for t, u in anchors
               if not re.search(r'tulostus|pöytäkirj|selostus|muistio|päätöshisto|lausunto|esityslist|'
                                r'sijaintikartta|sijainti|ilmakuva|viisto|havainne|yleiskartta|opaskartta|'
                                r'kaupunginosakartta', t)]
    for t, u in anchors:                       # tier 1: the plan drawing itself
        if re.search(r'piirustus|kaavakartta|asemakaavakartta|suunnitelmapiirustus', t):
            return u
    for t, u in anchors:                       # tier 2: any remaining plan map (not a locator)
        if re.search(r'kartta|suunnitelma', t):
            return u
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dm", default="u540")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--nmax", type=int, default=45)
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()
    out = args.out or f"{OUT}/plans_{args.year}.kml"

    print(f"[1/3] listing {args.dm} meetings for {args.year} (from January) ...")
    meetings = list_meetings(args.dm, args.year, args.nmax, verbose=False)
    print(f"      {len(meetings)} meetings")

    print("[2/3] scraping + classifying (dropping admin items) ...")
    seen = set()
    items = {k: [] for k, *_ in TYPES}
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
            items[key].append(dict(title=re.sub(r'^\s*\d+\.\s*/\s*\d+\s*§\s*', '', txt),
                                   decision="https://paatokset.hel.fi" + m.group(1),
                                   month=int(mo), year=int(y), date=mtg["date"]))
    for k, label, *_ in TYPES:
        print(f"      {len(items[k]):3}  {label}")

    print("[3/3] per-item: decision page -> PDF + geocode ...")
    gcache = {}
    folders = []
    for key, label, icon, _m in TYPES:
        pins, skipped = [], 0
        for d in items[key]:
            page = decision_page(d["decision"])
            pdf = extract_pdf(page)
            # location: agenda title first, else the decision page text
            loc = loc_from_text(d["title"]) or loc_from_text(re.sub(r'<[^>]+>', ' ', page[:9000]))
            if not loc:
                skipped += 1
                continue
            if loc not in gcache:
                gcache[loc] = geocode(loc, loc)
            lat, lon, conf = gcache[loc]
            if lat is None:
                skipped += 1
                continue
            cap = f'{html.escape(loc)} ({MONTHS[d["month"]]} {d["year"]})'
            pdf_line = f'<a href="{pdf}">Open plan drawing (PDF)</a><br/>' if pdf else ""
            desc = ("<![CDATA["
                    f'{html.escape(d["title"])}<br/>Decision date: {d["date"]}<br/>'
                    f'{pdf_line}<a href="{d["decision"]}">Decision page</a><br/>'
                    f'<i>approx: {conf}-level</i>]]>')
            pins.append(f'<Placemark><styleUrl>#{key}</styleUrl>'
                        f'<name>{cap}</name><description>{desc}</description>'
                        f'<Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>')
        folders.append(f'<Folder><name>{label} ({len(pins)})</name>{"".join(pins)}</Folder>')
        print(f"  {label:34} {len(pins):3} pins ({skipped} skipped)")

    styles = "".join(
        f'<Style id="{k}"><IconStyle><Icon><href>{PADDLE.format(icon)}</href></Icon></IconStyle></Style>'
        for k, _l, icon, _m in TYPES)
    kml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           f'<name>Helsinki plans {args.year} — Kaupunkiympäristölautakunta</name>'
           + styles + "".join(folders) + '</Document></kml>')
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(kml)
    total = sum(f.count("<Placemark>") for f in folders)
    print(f"\nwrote {total} pins across {len(TYPES)} layers -> {out}  (with PDF links)")


if __name__ == "__main__":
    main()
