#!/usr/bin/env python3
"""
Pre-2017 committee plan decisions — from Helsinki's **live static decision
repository** (`www.hel.fi/static/public/hela/`), which still serves the päätös
bulletins and their attachment PDFs (the plan DRAWINGS) going back to 2012. This
is how the drawings reach back before the 2017 decision records (paatokset.hel.fi
only indexes 2017+; the OpenAhjo API and the per-meeting ZIP bundles are dead).

Enumeration (no API, no directory listing — both blocked):
  - meeting manifest per committee comes from the Internet Archive capture of the
    old `openhelsinki.hel.fi/files/<committee>/` listing → (date, meeting number);
  - each meeting's **Päätöstiedote** index is at a derivable, GUID-free path:
      {HELA}/{folder}/Suomi/Paatostiedote/{year}/{PREF}_{date}_{ABBR}_{n}_Pt/index.html
    and lists every agenda item (title + its decision PDF + named `Liite.pdf` attachments).

Covers the two pre-reform plan committees:
  Kaupunkisuunnittelulautakunta (zoning/traffic) · Yleisten töiden lautakunta (street/park).

Records match the decision dataset schema and are written to a SEPARATE file by
default so you can review before merging into plans_dataset.json.

    python3 -m lautakuntamuistiot.scrape_decisions_2013 --committee ksv
    python3 -m lautakuntamuistiot.scrape_decisions_2013 --committee ytlk
"""
import urllib.request, re, json, argparse, os, time, html as _html

from .common import classify, EXCLUDE, TYPES
from .locate import locate, load_cache, save_cache
from .settings import OUT, USER_AGENT

HELA = "https://www.hel.fi/static/public/hela"
WB = "http://web.archive.org/web/20210616085555/https://openhelsinki.hel.fi/files/{}/"
UA = {"User-Agent": "Mozilla/5.0 " + USER_AGENT}
LABEL = {k: lbl for k, lbl, *_ in TYPES}

COMMITTEES = {
    "ksv":  dict(name="Kaupunkisuunnittelulautakunta", folder="Kaupunkisuunnittelulautakunta",
                 wbdir="Kaupunkisuunnittelulautakunta_51100", pref="Ksv", abbr="Kslk", dm="51100"),
    "ytlk": dict(name="Yleisten töiden lautakunta", folder="Yleisten_toiden_lautakunta",
                 wbdir="Yleisten%20toiden%20lautakunta_52100", pref="HKR", abbr="Ytlk", dm="52100"),
}
DATASET = f"{OUT}/plans_pre2017_dataset.json"
GCACHE = f"{OUT}/geocode_cache.json"

# strip committee/"esitys"/"lausunto" boilerplate so the area is first in the title
_PREFIX = re.compile(r'^(?:Kaupunkisuunnittelulautakunnan|Yleisten töiden lautakunnan)?\s*'
                     r'(?:tarkistettu\s+)?(?:esitys|lausunto|päätös)\s+', re.I)


def location_of(title, cache):
    return locate(cache, _PREFIX.sub("", title))


def fetch(url, n=400000):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
            return r.status, r.read(n).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def meetings(cfg):
    """[(date 'YYYY-MM-DD', number)] from the Wayback meeting manifest, oldest first."""
    _, body = fetch(WB.format(cfg["wbdir"]), 400000)
    pat = re.escape(cfg["pref"]) + r' (\d{4}-\d{2}-\d{2}) ' + re.escape(cfg["abbr"]) + r' (\d+) Pk'
    seen = {}
    for date, num in re.findall(pat, body):
        seen[(date, num)] = (date, int(num))
    return sorted(seen.values(), key=lambda x: x[0])


def parse_index(h):
    """[(title, decision_url, [(attachment_name, liite_url)])] in agenda order."""
    items, cur = [], None
    for m in re.finditer(r'<a href="(/static/public/hela/[^"]+\.pdf)"[^>]*>(.*?)</a>', h, re.S):
        url, fn = m.group(1), m.group(1).split("/")[-1]
        if fn == "Liite.pdf":
            if cur:
                name = re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', ' ', m.group(2)))).strip()
                cur[2].append((name or "Liite", "https://www.hel.fi" + url))
            continue
        # a named decision PDF opens a new item; title = nearest preceding real span
        pre = h[:m.start()]
        spans = re.findall(r'<span[^>]*>([^<]{4,300})</span>', pre)
        title = ""
        for s in reversed(spans):
            s = re.sub(r'\s+', ' ', _html.unescape(s)).strip()
            if s and s.lower() not in ("pdf", "html"):
                title = s; break
        cur = (title, "https://www.hel.fi" + url, [])
        items.append(cur)
    return items


# Attachments come in agenda order, usually "Sijaintikartta" (location map) first —
# rank by name so the pin links the plan drawing itself, as extract_pdf() does for 2017→.
NOT_DRAWING = re.compile(r'sijainti|ilmakuva|viisto|opaskartta|yleiskartta|selostus|raportti|'
                         r'muistio|muutokset|kustannus|lausun|vastine|mielipi|kirje|pöytäkirj|'
                         r'luettelo|taulukko|ohjelma|tiivistelmä|esitys\b|päätös|selvitys|lähtötied|tilasto', re.I)
DRAWING_TIERS = (
    re.compile(r'piirustus|kaavakartta|kaavaehdotuksen?\b.*kartta|muutosehdotuksen?\b.*kartta|'
               r'kaavan\b.*kartta|kaavarunko\b|(katu|liikenne|puisto|yleis)suunnitelma|suunnitelmakartta', re.I),
    re.compile(r'kartta|suunnitelma|luonnos|liikennejärjestely|periaatteet', re.I),
    re.compile(r'havainne|leikkaus|julkisivu|näkymä', re.I),
)


def best_drawing(liites):
    """URL of the attachment that is the plan drawing, or None (never a location map)."""
    cands = [(n, u) for n, u in liites if not NOT_DRAWING.search(n)]
    for tier in DRAWING_TIERS:
        for n, u in cands:
            if tier.search(n):
                return u
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--committee", choices=list(COMMITTEES), required=True)
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--cache", default=GCACHE)
    args = ap.parse_args()
    cfg = COMMITTEES[args.committee]

    ds = json.load(open(args.dataset, encoding="utf-8")) if os.path.exists(args.dataset) \
        else {"generated": None, "records": []}
    ds.setdefault("unlocated", [])
    cache = load_cache(args.cache)
    unloc = {(u["dm"], u["decision_url"]): u for u in ds["unlocated"]}
    bykey = {(r["dm"], r["decision_url"]): i for i, r in enumerate(ds["records"])}

    mtgs = meetings(cfg)
    print(f"[{args.committee}] {cfg['name']}: {len(mtgs)} meetings "
          f"({mtgs[0][0]}..{mtgs[-1][0]})")

    added = skipped = nomtg = nloc = 0
    for date, num in mtgs:
        yr = date[:4]
        folder = f'{cfg["pref"]}_{date}_{cfg["abbr"]}_{num}_Pt'
        st, h = fetch(f'{HELA}/{cfg["folder"]}/Suomi/Paatostiedote/{yr}/{folder}/index.html')
        if st != 200 or not h:
            nomtg += 1
            continue
        mo = int(date[5:7])
        for title, dec_url, liites in parse_index(h):
            if not title or EXCLUDE.search(title):
                skipped += 1; continue
            key = classify(title.lower())
            if not key:
                skipped += 1; continue
            loc, lat, lon, conf = location_of(title, cache)
            guid = re.search(r'/([0-9A-F-]{36})/', dec_url, re.I)
            rec = dict(committee=cfg["name"], dm=cfg["dm"],
                       asia_id="hela-" + (guid.group(1).lower() if guid else dec_url[-40:]),
                       plan_type=key, plan_type_label=LABEL[key], heading=title, title=title,
                       summary=None, date=f"{date[8:10]}.{date[5:7]}.{yr}",
                       year=int(yr), month=mo, location=loc, lat=lat, lon=lon, geocode=conf,
                       decision_url=dec_url, map_url=best_drawing(liites),
                       attachments=liites)
            k = (cfg["dm"], dec_url)
            if lat is None:                     # keep it visible for review, off the map
                unloc[k] = rec; nloc += 1; continue
            unloc.pop(k, None)
            if k in bykey:
                ds["records"][bykey[k]] = rec
            else:
                bykey[k] = len(ds["records"]); ds["records"].append(rec); added += 1

    ds["unlocated"] = list(unloc.values())
    ds["generated"] = time.strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(args.dataset) or ".", exist_ok=True)
    json.dump(ds, open(args.dataset, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    save_cache(cache, args.cache)
    withmap = sum(1 for r in ds["records"] if r["map_url"])
    print(f"  +{added} plan records, {skipped} non-plan items, {nloc} unlocated, "
          f"{nomtg} meetings with no Pt index")
    print(f"  dataset now {len(ds['records'])} records ({withmap} with drawing) -> {args.dataset}")


if __name__ == "__main__":
    main()
