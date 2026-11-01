#!/usr/bin/env python3
"""
Sanity-check the plans KML pins against the decisions' WRITTEN material.

The geocoding is heuristic (a token from the title), so a pin can land on the wrong
feature even inside Helsinki. This validates each pin two ways:

  1. inside the Helsinki bbox,
  2. the pin's actual neighbourhood/road (reverse-geocoded) is actually MENTIONED in
     the decision's written text (the meeting material). If the place where the pin
     landed isn't named in the decision, the geocode is suspect.

Prints a flagged list (title, coordinate, what the pin sits on, what the decision
says) so the doubtful ones can be eyeballed. Read-only; hits Nominatim at <=1/s.

    python3 check_locations.py [-k output/plans_2025.kml]
"""
import re, json, urllib.request, urllib.parse, time, argparse

from settings import OUT, USER_AGENT

UA = {"User-Agent": USER_AGENT}
HKI = (60.10, 60.30, 24.78, 25.27)


def reverse(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse?" + urllib.parse.urlencode(
        {"lat": lat, "lon": lon, "format": "json", "zoom": 16, "addressdetails": 1})
    try:
        return json.load(urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=20)).get("address", {})
    except Exception:
        return {}


def fetch(u):
    try:
        return urllib.request.urlopen(
            urllib.request.Request(u.split("?")[0], headers=UA), timeout=20).read().decode("utf-8", "ignore")
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", "--kml", default=f"{OUT}/plans_2025.kml")
    args = ap.parse_args()
    h = open(args.kml, encoding="utf-8").read()

    pins = []
    for m in re.finditer(
            r'<name>([^<]+)</name><description><!\[CDATA\[(.*?)\]\]></description>'
            r'<Point><coordinates>([-0-9.]+),([-0-9.]+)', h, re.S):
        name, desc = m.group(1), m.group(2)
        title = desc.split("<br/>")[0].strip()
        dm = re.search(r'href="(https://paatokset\.hel\.fi[^"]+)"', desc)
        pins.append((name, title, float(m.group(4)), float(m.group(3)), dm.group(1) if dm else ""))

    print(f"checking {len(pins)} pins against decision text ...\n")
    page_cache, suspects, ok = {}, [], 0
    for name, title, lat, lon, dec in pins:
        inbox = HKI[0] <= lat <= HKI[1] and HKI[2] <= lon <= HKI[3]
        addr = reverse(lat, lon); time.sleep(1.1)
        cand = [addr.get(x, "") for x in ("road", "neighbourhood", "quarter", "suburb", "city_district", "town")]
        cand = [c for c in cand if c]
        if dec not in page_cache:
            page_cache[dec] = fetch(dec).lower()
        page = page_cache[dec]
        matched = next((c for c in cand if c.lower() in page), None)
        if inbox and matched:
            ok += 1
        else:
            suspects.append((name, title, lat, lon, cand, matched, inbox, dec))

    print(f"RESULT: {ok} corroborated, {len(suspects)} SUSPECT (of {len(pins)})\n")
    for name, title, lat, lon, cand, matched, inbox, dec in suspects:
        why = ("outside Helsinki" if not inbox
               else "pin's area not named in the decision text")
        print(f"  ⚠ {name}  [{why}]")
        print(f"      plan:  {title[:72]}")
        print(f"      pin:   {lat:.4f},{lon:.4f}  sits on: {', '.join(cand[:3]) or '—'}")
        print(f"      {dec.split('?')[0]}")


if __name__ == "__main__":
    main()
