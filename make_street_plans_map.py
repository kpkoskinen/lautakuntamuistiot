#!/usr/bin/env python3
"""
Street-plan decision map (first proof of concept).

Builds a Google My Maps / KML file with one RED pin per Helsinki street-plan
(katusuunnitelma) committee decision from roughly the past two years: a rough
geocoded location + a short description + a link to the decision (which holds the
plan-drawing PDFs) and, where known, a direct plan-PDF link.

WHY: the plan-drawing PDFs (ahjojulkaisu.hel.fi, attached to
Kaupunkiympäristölautakunta decisions on paatokset.hel.fi) carry NO georeference
and NO reliable machine-readable street name (vectorised text). But the *decision*
states the street + district in plain text, so we geocode from the decision.

Locations are ROUGH (street-level) — each pin is tagged with a confidence.

OUTPUT GOES TO output/ AND IS NEVER COMMITTED. Only this script + README live in the
repo. Run:
    python3 make_street_plans_map.py        # -> output/street_plans.kml
    python3 make_street_plans_map.py -o PATH
"""
import urllib.request, urllib.parse, json, time, argparse, os, html

from settings import OUT, USER_AGENT

# ── Best-effort set of katusuunnitelma decisions, ~past two years (2024–2026) ──
# Gathered from paatokset.hel.fi search. NOT guaranteed exhaustive — extend freely
# (see README for how to automate full enumeration). `street` = primary street for
# geocoding; `pdf` optional (direct plan drawing) else the decision page holds it.
D = "https://paatokset.hel.fi/fi/asia/"
DECISIONS = [
    # 2026
    dict(street="Naantalintie", district="Munkkiniemi", year=2026, plan="32565/1",
         decision=D+"hel-2026-005091/358536b4-939d-c831-bbba-a06067e00004",
         pdf="https://ahjojulkaisu.hel.fi/CE6249B9-0F6D-CB5E-94EE-9E1F63300000.pdf"),
    dict(street="Vihdintie", district="Haaga", year=2026, plan="32388/4",
         decision=D+"hel-2026-002273/f2ee4aed-f3d5-423c-bc14-781fb5536f4e",
         pdf="https://ahjojulkaisu.hel.fi/16119109-4A68-C368-949D-9D4D2AA00000.pdf"),
    dict(street="Itäväylä", district="Herttoniemi", year=2026, plan="32297/1",
         decision="https://paatokset.hel.fi/en/node/252076",
         pdf="https://ahjojulkaisu.hel.fi/14DDB72B-F724-C6DA-AB01-9A6D44900000.pdf"),
    dict(street="Viilarintie", district="Vartiokylä", year=2026, plan="32315/1",
         decision="https://paatokset.hel.fi/en/node/252076",
         pdf="https://ahjojulkaisu.hel.fi/4DCAFFEE-45D5-CDDA-9D15-9A6D5EE00001.pdf"),
    # 2025
    dict(street="Käsityöläisentie", district="Suutarila", year=2025,
         decision=D+"hel-2025-003079/bf5b523f-373a-c923-abe6-96c3f1b00002"),
    dict(street="Linnankoskenkatu", district="Taka-Töölö", year=2025,
         decision=D+"hel-2025-012656/85db6e22-b74b-4d8e-b11b-e7f763ab219a"),
    dict(street="Karamzininranta", district="Kluuvi", year=2025,
         decision=D+"hel-2025-009163/8ccd1534-ebc8-435d-ab02-90a6e2383993"),
    dict(street="Toukolankatu", district="Toukola", year=2025,
         decision=D+"hel-2025-008120/ecc7509a-1be7-4757-bca0-f1e3314b92ff"),
    dict(street="Saukonlaituri", district="Jätkäsaari", year=2025,
         decision=D+"hel-2025-007121/e5406ec4-307c-46ca-ae19-43d4595bdcc8"),
    dict(street="Huopalahdentie", district="Munkkiniemi", year=2025,
         decision=D+"hel-2025-017745/64b70a07-defe-ca3c-8560-9cfa97a00000"),
    dict(street="Suvilahdenkatu", district="Sörnäinen", year=2025,
         decision=D+"hel-2025-009167/9a9144e4-28d3-c8d7-90bf-9cfa97900004"),
    dict(street="Vihdintie", district="Haaga", year=2025,
         decision=D+"hel-2025-018691/30a23d62-d001-ceb9-b6c5-9cfa97b00002"),
    # 2024
    dict(street="Mannerheiminaukio", district="Kluuvi", year=2024, plan="32217/1",
         decision=D+"hel-2024-014830/ebc49d33-0de4-ccc3-ad4b-96c3f1900004"),
    dict(street="Paciuksenkaari", district="Meilahti", year=2024, plan="31783/1",
         decision=D+"hel-2024-002200/017cb9d2-b6c7-c8ab-bba9-9000a9a00002"),
    dict(street="Meri-Rastilan tie", district="Vuosaari", year=2024,
         decision=D+"hel-2024-002193/075ee0ae-4767-4fe0-8846-ab12b17b220a"),
    dict(street="Ahdinranta", district="Jätkäsaari", year=2024, plan="32037/1",
         decision=D+"hel-2024-002476/93f405d1-7ec5-41bd-8e8c-49c764806194",
         pdf="https://ahjojulkaisu.hel.fi/6BB03B92-784D-CDC9-A1B6-956607900000.pdf"),
    dict(street="Albumikatu", district="Hermanni", year=2024,
         decision=D+"hel-2024-002023/c2d8978c-7ba9-41c6-a4e2-22cbd6cda489"),
    dict(street="Neptunuksenkatu", district="Jätkäsaari", year=2024,
         decision=D+"hel-2024-013924/91410e3f-4598-cca5-a8bd-94f98c800006"),
    dict(street="Länsimäentie", district="Mellunkylä", year=2024,
         decision=D+"hel-2024-008416/cdb64f0a-2537-4a17-8f23-2aa93484233f"),
]

UA = {"User-Agent": USER_AGENT}
RED_ICON = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"

# Helsinki bounding box (minlat, maxlat, minlon, maxlon) — covers all districts +
# islands. Results outside it are rejected (a bare token like "Valimon" otherwise
# matches a same-named place in a neighbouring municipality).
HKI_BBOX = (60.10, 60.30, 24.78, 25.27)
_VIEWBOX = "24.78,60.30,25.27,60.10"     # Nominatim lon1,lat1,lon2,lat2


def _nominatim(params):
    params = {**params, "viewbox": _VIEWBOX}          # bias toward Helsinki
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25))
        if r:
            lat, lon = float(r[0]["lat"]), float(r[0]["lon"])
            if HKI_BBOX[0] <= lat <= HKI_BBOX[1] and HKI_BBOX[2] <= lon <= HKI_BBOX[3]:
                return lat, lon
            return None                               # reject out-of-Helsinki match
    except Exception:
        return None
    return None


def geocode(street, district):
    """Tiered: street-in-Helsinki -> district-in-Helsinki. Returns (lat, lon, confidence)."""
    p = _nominatim({"street": street, "city": "Helsinki", "country": "Finland",
                    "format": "json", "limit": 1})
    time.sleep(1.1)                              # Nominatim policy: <= 1 req/s
    if p:
        return p[0], p[1], "street"
    p = _nominatim({"q": f"{district}, Helsinki, Finland", "format": "json", "limit": 1})
    time.sleep(1.1)
    if p:
        return p[0], p[1], "district"
    return None, None, "none"


def placemark(d, lat, lon, conf):
    plan = f'Piirustus {html.escape(d["plan"])}<br/>' if d.get("plan") else ""
    pdf = f'<a href="{d["pdf"]}">Open plan PDF</a><br/>' if d.get("pdf") else ""
    desc = ("<![CDATA["
            f'Katusuunnitelma — {html.escape(d["district"])} ({d["year"]})<br/>'
            f'{plan}{pdf}'
            f'<a href="{d["decision"]}">Decision page (plan PDFs here)</a><br/>'
            f'<i>approx location: {conf}-level</i>'
            "]]>")
    return (f'<Placemark><styleUrl>#rw</styleUrl>'
            f'<name>{html.escape(d["street"])} ({d["year"]})</name>'
            f'<description>{desc}</description>'
            f'<Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out",
                    default=f"{OUT}/street_plans.kml")
    args = ap.parse_args()

    pins, skipped = [], []
    for d in DECISIONS:
        lat, lon, conf = geocode(d["street"], d["district"])
        if lat is None:
            skipped.append(f'{d["street"]} ({d["year"]})')
            continue
        pins.append(placemark(d, lat, lon, conf))
        print(f"  {d['street']:18} {d['year']} -> {lat:.5f},{lon:.5f}  ({conf})")

    style = (f'<Style id="rw"><IconStyle><color>ff0000ff</color>'
             f'<Icon><href>{RED_ICON}</href></Icon></IconStyle></Style>')
    kml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'
           '<name>Helsinki street plans (katusuunnitelmat) 2024–2026</name>'
           + style + "".join(pins) + '</Document></kml>')

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        f.write(kml)
    print(f"\nwrote {len(pins)} RED pins -> {args.out}")
    if skipped:
        print("  could not geocode (add manually / use Digitransit):", skipped)


if __name__ == "__main__":
    main()
