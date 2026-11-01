#!/usr/bin/env python3
"""
Public consultations ("Kerro kantasi", kerrokantasi.hel.fi) about plans, with their
drawings — a second source next to the committee decisions.

Open API, no key:  https://kerrokantasi.api.hel.fi/v1/hearing/   (2014→, ~400 hearings)
Each hearing has a title, abstract, open/close dates, labels, usually an area
geometry (`geojson`), and sections carrying images (plan drawings, sketches,
aerial views — mixed with photos) and sometimes PDF attachments (`files`).

We keep the plan-related hearings (city-environment topics; schools, budgets,
mayor's evenings, Q&A events are dropped), place each at the centroid of its
geometry — or locate its title with locate when it has none — and list the
drawings: every PDF attachment and every image that isn't just a photo.

    python3 -m lautakuntamuistiot.scrape_consultations            # -> output/kerrokantasi_dataset.json
"""
import urllib.request, json, re, argparse, time, os, html

from .common import classify, GCACHE
from .locate import locate, load_cache, save_cache, HKI_BBOX
from .settings import OUT, USER_AGENT

API = "https://kerrokantasi.api.hel.fi/v1/hearing/"
PAGE = "https://kerrokantasi.hel.fi/{}"
DATASET = f"{OUT}/kerrokantasi_dataset.json"
UA = {"User-Agent": USER_AGENT}

# topic filter over title + labels
PLAN = re.compile(r'kaav|suunnitel|liikenne|pyörä|raitio|katu|kadu|puisto|tori\b|aukio|ranta|silta|'
                  r'väylä|\btie\b|tien\b|bulevard|kortteli|alue|maankäyt|täydennysrak|leikkipaik|'
                  r'kilpailu|uudistu|asumista|rakentami', re.I)
NOT_PLAN = re.compile(r'koulu|oppilaaksiotto|päiväkot|pormestari|asukasilta|talousarvi|budjet|'
                      r'strategi|palveluverkko|terveys|pelastus|kirjasto|nuoriso|osallisuusmalli|'
                      r'verkkotilaisuu|asukastilaisuu|kysy etukäteen|tarkastuslautakun|avustus|'
                      r'ilmastovahd|tontinluovutu|opaste', re.I)
NOT_ORG = ("Kasvatuksen", "Sosiaali", "Tarkastus", "Kulttuurin", "Kaupunginkanslia")
# an image is a drawing unless its caption only credits a photographer
PHOTO = re.compile(r'kuva(?:aja)?\s*:|kuvaaja|valokuva|unsplash|helsinki marketing|kuvatoimisto|'
                   r'aineistopankki|©|\(\s*[^()]*/\s*[A-ZÅÄÖ][\w-]+ [A-ZÅÄÖ][\w-]+\s*\)\s*$', re.I)
# stock-photo sources are photos whatever the caption says about plans
STOCK_PHOTO = re.compile(r'aineistopankki|unsplash|valokuva', re.I)
DRAWING = re.compile(r'suunnitel|luonnos|kartta|havainne|kaava|vaihtoehto|rajat|rajaus|ilmakuva|'
                     r'leikkaus|plan|periaate|visio|ehdotu|näkymä', re.I)


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(url)


def fi(d):
    d = d or {}
    return (d.get("fi") or d.get("en") or d.get("sv") or "").strip()


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def is_plan(h):
    t = fi(h["title"]) + " " + " ".join(fi(l.get("label")) for l in h.get("labels", []))
    return bool(PLAN.search(t)) and not NOT_PLAN.search(t) \
        and not (h.get("organization") or "").startswith(NOT_ORG)


def _rings(g):
    """Every exterior ring / point of a GeoJSON object, as lists of (lon, lat)."""
    t = g.get("type")
    if t == "FeatureCollection":
        return [r for f in g.get("features", []) for r in _rings(f.get("geometry") or {})]
    if t == "Feature":
        return _rings(g.get("geometry") or {})
    if t == "Point":
        return [[tuple(g["coordinates"][:2])]]
    if t in ("LineString", "MultiPoint"):
        return [[tuple(c[:2]) for c in g["coordinates"]]]
    if t == "Polygon":
        return [[tuple(c[:2]) for c in g["coordinates"][0]]]
    if t in ("MultiPolygon",):
        return [[tuple(c[:2]) for c in p[0]] for p in g["coordinates"]]
    if t == "MultiLineString":
        return [[tuple(c[:2]) for c in l] for l in g["coordinates"]]
    if t == "GeometryCollection":
        return [r for x in g.get("geometries", []) for r in _rings(x)]
    return []


def centroid(g):
    """(lat, lon, span_km) — area-weighted centroid of the polygons (vertex mean for
    points/lines); span_km is the bbox diagonal, to tell a block from a city-wide area."""
    pts = [p for r in _rings(g) for p in r]
    if not pts:
        return None
    A = cx = cy = 0.0
    for r in _rings(g):
        for (x0, y0), (x1, y1) in zip(r, r[1:]):
            c = x0 * y1 - x1 * y0
            A += c; cx += (x0 + x1) * c; cy += (y0 + y1) * c
    if abs(A) > 1e-12:
        lon, lat = cx / (3 * A), cy / (3 * A)
    else:
        lon, lat = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    span = ((max(xs) - min(xs)) * 55.6) ** 2 + ((max(ys) - min(ys)) * 111.3) ** 2
    return lat, lon, span ** 0.5


def drawings(h):
    """[(label, url)] — PDF attachments first, then images that aren't plain photos."""
    out, seen = [], set()
    for s in h.get("sections", []):
        for f in s.get("files", []):
            if f.get("url") and f["url"] not in seen:
                seen.add(f["url"]); out.append((fi(f.get("title")) or "Liite (PDF)", f["url"]))
    for s in h.get("sections", []):
        for im in s.get("images", []):
            cap = fi(im.get("caption")) or fi(im.get("title"))
            if not im.get("url") or im["url"] in seen:
                continue
            if STOCK_PHOTO.search(cap) or (PHOTO.search(cap) and not DRAWING.search(cap)):
                continue
            seen.add(im["url"]); out.append((cap[:120] or fi(s.get("title")) or "Kuva", im["url"]))
    return out


def short_title(t):
    """'Puimuripuisto ja Tilketori' from 'Puimuripuisto ja Tilketori – kerro näkemyksesi!'"""
    t = re.split(r'\s+[–—-]\s+|[!?]', t)[0].strip()
    return t if len(t) <= 70 else t[:67].rsplit(" ", 1)[0] + "…"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--cache", default=GCACHE)
    args = ap.parse_args()
    cache = load_cache(args.cache)

    lst, url = [], API + "?limit=100"
    while url:
        d = get(url); lst += d["results"]; url = d["next"]
    plans = [h for h in lst if h.get("published", True) and is_plan(h)]
    print(f"[kerrokantasi] {len(lst)} hearings -> {len(plans)} plan-related", flush=True)

    records, unloc = [], []
    for h in plans:
        h = get(API + (h.get("slug") or h["id"]) + "/"); time.sleep(0.2)
        title = fi(h["title"])
        summary = text(fi(h.get("abstract")))
        t = time.strptime(h["open_at"][:10], "%Y-%m-%d")
        close = h.get("close_at") and time.strftime("%d.%m.%Y", time.strptime(h["close_at"][:10], "%Y-%m-%d"))
        base = dict(committee="Kerro kantasi", dm="kerrokantasi", asia_id="kk-" + h["id"], stage="consultation",
                    plan_type="kerrokantasi", subtype=classify(title.lower()),
                    heading=title, title=title, summary=summary,
                    date=time.strftime("%d.%m.%Y", t), close_date=close,
                    year=t.tm_year, month=t.tm_mon,
                    decision_url=PAGE.format(h.get("slug") or h["id"]),
                    labels=[fi(l.get("label")) for l in h.get("labels", []) if fi(l.get("label"))],
                    drawings=drawings(h))
        base["map_url"] = base["drawings"][0][1] if base["drawings"] else None
        # the validated place name makes the label ("Hämeentie", not "Millainen on
        # Hämeentien tulevaisuus"); the hearing's own area, when it has one, gives the point
        loc, lat, lon, conf = locate(cache, title, fallback=(summary,))
        label = loc or short_title(title)
        c = centroid(h["geojson"]) if h.get("geojson") else None
        if c and HKI_BBOX[0] <= c[0] <= HKI_BBOX[1] and HKI_BBOX[2] <= c[1] <= HKI_BBOX[3]:
            rec = dict(base, location=label, lat=c[0], lon=c[1],
                       geocode="area", area_km=round(c[2], 2))
        elif lat is not None:
            rec = dict(base, location=label, lat=lat, lon=lon, geocode=conf)
        else:
            unloc.append(base); continue
        records.append(rec)

    ds = {"generated": time.strftime("%Y-%m-%d"), "source": API,
          "records": records, "unlocated": unloc}
    os.makedirs(os.path.dirname(args.dataset) or ".", exist_ok=True)
    json.dump(ds, open(args.dataset, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    save_cache(cache, args.cache)
    print(f"  {len(records)} placed ({sum(r['geocode'] == 'area' for r in records)} from the hearing's "
          f"own area), {len(unloc)} unlocated, "
          f"{sum(bool(r['drawings']) for r in records)} with drawings "
          f"({sum(len(r['drawings']) for r in records)} drawings) -> {args.dataset}")


if __name__ == "__main__":
    main()
