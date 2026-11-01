#!/usr/bin/env python3
"""
Location heuristics for plan decisions: title/heading text -> (place, lat, lon, kind).

Replaces the old "first capitalised token" approach, which on Finnish titles mostly
picked a GENITIVE ("Kalasataman katusuunnitelmien hyväksyminen" -> "Kalasataman").
Nominatim then fuzzy-matched that to some POI ("Kalasataman kirjasto") or to the city
itself ("Helsingin"), and tagged it "street" — so dozens of plans piled onto one point.

What this does instead:
  1. Candidates, most specific first: street/park/square names (any inflection,
     restored to the nominative: Caloniuksenkadun -> Caloniuksenkatu), then area
     names — the trailing district chunks of the title ("…, Haaga, Pitäjänmäki")
     and genitive area words (Kalasataman -> Kalasatama, Vuosaaren -> Vuosaari).
  2. Each candidate is geocoded inside Helsinki and ACCEPTED only if the result's
     name equals the candidate and it is the right kind of feature. The kind is read
     from the OSM class, not assumed:
        street   — a road (highway=*)
        place    — a park, square or other small named area
        district — a neighbourhood / suburb / island
     Whole-city / municipality matches are rejected.
  3. MANUAL holds hand-fixed coordinates that OSM can't resolve.

Cache: one entry per candidate query, so re-runs are offline and reproducible.
"""
import json, re, time, urllib.parse, urllib.request

from settings import USER_AGENT

UA = {"User-Agent": USER_AGENT}
_VIEWBOX = "24.78,60.30,25.27,60.10"            # Helsinki, lon1,lat1,lon2,lat2
HKI_BBOX = (60.10, 60.30, 24.78, 25.27)

# hand-fixed points (OSM lacks them / ambiguous); value = (lat, lon)
MANUAL = {
    "Lehtisaarentie": (60.1817, 24.8546),          # the plan section, not the street's far end
    "Pyhän Laurin puisto": (60.1817, 24.8546),
    "Loviseholminpuisto": (60.1813, 24.9768),
}

# street / park / square words (nominative stems). A compound ending in one of
# these is a specific named place.
_PLACE_SUFFIX = (r'katu|tie|kuja|polku|väylä|aukio|tori|silta|ranta|kaari|rinne|laituri|'
                 r'penger|puisto|puistikko|raitti|portti|kenttä|bulevardi|esplanadi|'
                 r'tunneli|piha|terassi|reitti|baana')
# (mäki/kallio/lehto/metsä… are deliberately NOT here: in titles they are mostly
#  area names — "Pitäjänmäen Sulkapolun …" — and are picked up as area candidates.)
# inflected stem forms -> nominative (consonant gradation etc.), applied on word end
_NOM = [
    (r'kadu(?:n|t|lla|lle|lta|ille|ista|illa|jen)$', 'katu'),
    (r'kaduilla$', 'katu'),
    (r'tie(?:n|t|llä|lle|ltä|iden|ille)$', 'tie'),
    (r'teiden$', 'tie'),
    (r'polu(?:n|t|lla|lle)$', 'polku'),
    (r'sillan$|sillat$|siltojen$', 'silta'),
    (r'rannan$|rannat$|rantojen$', 'ranta'),
    (r'kaaren$|kaaret$', 'kaari'),
    (r'rinteen$|rinteet$', 'rinne'),
    (r'penkereen$', 'penger'),
    (r'mäen$|mäet$', 'mäki'),
    (r'lahden$', 'lahti'),
    (r'joen$', 'joki'),
    (r'saaren$|saarten$', 'saari'),
    (r'niemen$', 'niemi'),
    (r'järven$', 'järvi'),
    (r'kosken$', 'koski'),
    (r'vuoren$', 'vuori'),
    (r'nummen$', 'nummi'),
    (r'kummun$', 'kumpu'),
    (r'pellon$', 'pelto'),
    (r'lehdon$', 'lehto'),
    (r'kankaan$', 'kangas'),
    (r'tammen$', 'tammi'),
    (r'kentän$|kentät$', 'kenttä'),
    (r'portin$', 'portti'),
    (r'raitin$', 'raitti'),
    (r'kallion$', 'kallio'),
    (r'kulman$', 'kulma'),
    (r'kärjen$', 'kärki'),
    (r'huipun$', 'huippu'),
    (r'laakson$', 'laakso'),
    (r'harjun$', 'harju'),
    (r'linjan$|linjat$', 'linja'),
]
# words that are never a location
NOT_PLACE = re.compile(
    r'^(?:helsin|kaupun|lautakun|kaupunkiympärist|kaupunkisuunnittelu|yleisten|esitys|'
    r'lausun|päätös|tarkistet|vastine|oikaisu|katusuunnitel|liikennesuunnitel|puistosuunnitel|'
    r'suunnitel|asemakaav|kaava|kaavoitus|kaavarun|periaat|muutos|nro|hyväksy|osayleiskaav|'
    r'yleiskaav|huoneisto|ratapiha|runkolinj|itäisen|läntisen|pohjoisen|eteläisen|uuden|'
    r'vanhan|ja$|sekä$|alue|kortteli|tontti|kiinteistö|maankäyttö|liikenne|pyöräliiken|'
    r'pysäköin|hulevesi|katu-|katu$|puisto$|tie$|raitiotie|joukkoliik|kehittämis|'
    r'toteutus|investoin|hanke|selvitys|ohjelma|a-asia|b-asia|helsinki|helsingfors)', re.I)
_ADMIN = re.compile(r'lautakun|kaupunkiympärist|oikaisu|talousarvi|maankäyttösopim|toimial|'
                    r'määrärah|hankinta|vuokra|valtuu|aloite|kokous|lausunt|esitys|'
                    r'toimintasuunnitelma|hallitukse|virastopääll|'
                    r'^leikkipuisto|^leikkialue|^liikuntapuisto', re.I)

_WORD = r"[A-ZÄÖÅ][\wäöåÄÖÅéü]*(?:-[A-ZÄÖÅa-zäöå][\wäöåÄÖÅéü]*)*"
_STREETISH = re.compile(rf"\b({_WORD}(?:{_PLACE_SUFFIX}|kadu|polu|sill|rann|kaare|rinte|"
                        rf"penkere|kentä)\w*)")


def nominatives(w):
    """Best-effort Finnish genitive/plural -> nominative variants for a place word,
    most likely first (each is only geocoded if the previous ones failed)."""
    for pat, rep in _NOM:
        if re.search(pat, w):
            return [re.sub(pat, rep, w)]
    out = []
    if re.search(r'ksen$', w):
        out.append(w[:-4] + "s")                       # Jollaksen -> Jollas
    if re.search(r'(?:n|t)$', w) and len(w) > 4 and w[-2] in "aeiouyäö":
        stem = w[:-1]
        out.append(stem)                               # Kalasataman -> Kalasatama
        if re.search(r'[aeiouyäö][kpt][aeiouyäö]$', stem):
            out.append(stem[:-1] + stem[-2] + stem[-1])  # Viikin -> Viikki, Kivikon -> Kivikko
        if w.endswith("in") and w[-3] not in "aeiouyäökpts":
            out.append(w[:-2])                         # Östersundomin -> Östersundom
    return out or [w]


def nominative(w):
    return nominatives(w)[0]


def candidates(*texts):
    """Ordered, de-duplicated [(name, tier)] — tier 'specific' (street/park) before 'area'."""
    spec, area = [], []
    for t in texts:
        if not t:
            continue
        t = re.sub(r'\((?:[ab]-asia|nro[^)]*|sisältää[^)]*)\)', ' ', t, flags=re.I)
        t = re.sub(r'[()]', ',', t)                      # "(Kaarela, Kuninkaantammi)" -> chunks
        for w in _STREETISH.findall(t):
            if NOT_PLACE.search(w) or _ADMIN.search(w):
                continue
            spec += nominatives(w)
        # two-word street names: "Capellan puistotien" -> "Capellan puistotie",
        # "Ida Aalbergin tie", "Aleksis Kiven katu"
        for a, b in re.findall(rf"((?:{_WORD}\s+)?{_WORD}n)\s+([a-zäöå]*(?:{_PLACE_SUFFIX}|kadu|polu|sill|rann|kaare|rinte)\w*)", t):
            bare = nominative(b) in ("katu", "tie", "puisto")   # NOT_PLACE alone, fine here
            if not NOT_PLACE.search(a.split()[-1]) and (bare or not NOT_PLACE.search(b)) \
                    and not _ADMIN.search(b):
                spec.append(f"{a} {nominative(b)}")
                if " " in a:
                    spec.append(f"{a.split()[-1]} {nominative(b)}")
        # named playgrounds / sports parks: "Leikkipuisto Traktori"
        for kind, n in re.findall(rf"\b(Leikkipuisto|Liikuntapuisto)\s+({_WORD})", t):
            spec.append(f"{kind} {n}")
        # two-word park names: "Pyhän Laurin puisto", "Kaisaniemen puisto"
        for a, b, c in re.findall(rf"({_WORD})(?:\s+({_WORD}))?\s+(puisto|puistikko|tori|aukio)\b", t):
            name = " ".join(x for x in (a, b) if x) + " " + c
            if not NOT_PLACE.search(a):
                spec.append(name)
        chunks = [c.strip() for c in t.split(",") if c.strip()]
        # trailing chunks are the district(s) in the modern title convention
        for c in reversed(chunks[1:]):
            w = c.split()[0] if c.split() else ""
            if len(c.split()) <= 2 and re.match(_WORD + "$", w) and not NOT_PLACE.search(w):
                area += nominatives(w)
        # genitive area words anywhere ("Kalasataman katusuunnitelmien …")
        for w in re.findall(_WORD, t):
            if not NOT_PLACE.search(w) and not _ADMIN.search(w) and len(w) > 3:
                area += nominatives(w)
    out, seen = [], set()
    for name, tier in [(n, "specific") for n in spec] + [(n, "area") for n in area]:
        if name.lower() not in seen:
            seen.add(name.lower()); out.append((name, tier))
    return out


# ── geocoding ────────────────────────────────────────────────────────────────
_BAD_PLACE = {"city", "municipality", "county", "state", "region", "country", "province"}
_AREA_TYPES = {"suburb", "quarter", "neighbourhood", "city_district", "borough",
               "island", "islet", "village", "hamlet", "locality", "isolated_dwelling"}


def _search(q, street=False):
    """Free-text search, or a structured street=/city= query (finds minor streets
    that free text fuzzes to a better-known neighbour: Myllypadontie -> Myllypurontie)."""
    params = dict(street=q, city="Helsinki") if street else dict(q=f"{q}, Helsinki")
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(dict(
        params, format="jsonv2", limit=5, viewbox=_VIEWBOX, bounded=1, countrycodes="fi"))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None                                          # network failure: don't cache


def _kind(hit):
    cat, typ, at = hit.get("category"), hit.get("type"), hit.get("addresstype")
    if at in _BAD_PLACE or typ in _BAD_PLACE:
        return None
    if cat == "highway":
        return "street"
    if at in _AREA_TYPES or typ in _AREA_TYPES or (cat == "boundary" and typ == "administrative"):
        return "district"
    if cat in ("railway", "public_transport") or typ in ("station", "stop", "platform"):
        return None                                      # "Kalasatama" metro ≠ the district
    if cat in ("leisure", "place", "landuse", "natural", "tourism", "amenity", "man_made",
               "bridge", "waterway", "historic", "boundary"):
        return "place"
    return None


def _norm(s):
    return re.sub(r'[\s–—-]+', ' ', re.sub(r'\(.*?\)', '', s)).strip().lower()


def _same_name(hit_name, name):
    """Exact match, ignoring spacing ("Longinojan puisto" = "Longinojanpuisto") and a
    leading "Helsingin" ("Helsingin keskuspuisto" = "Keskuspuisto")."""
    a, b = _norm(hit_name), _norm(name)
    a = re.sub(r'^helsingin ', '', a)
    return a.replace(" ", "") == b.replace(" ", "")


_STREET_NAME = re.compile(rf"(?:{_PLACE_SUFFIX})$", re.I)


def geocode_name(name, cache):
    """(lat, lon, kind) for an exact-name match in Helsinki, else (None, None, 'none')."""
    if name in MANUAL:
        return (*MANUAL[name], "manual")
    if name in cache:
        return tuple(cache[name])
    best = None
    for street in ((False, True) if _STREET_NAME.search(name) else (False,)):
        hits = _search(name, street)
        time.sleep(1.1)                                  # Nominatim policy: <= 1 req/s
        if hits is None:
            return None, None, "none"                    # network failure: not cached
        best = _pick(hits, name)
        if best:
            break
    res = list(best) if best else [None, None, "none"]
    cache[name] = res
    return tuple(res)


def _pick(hits, name):
    rank = {"street": 0, "place": 1, "district": 2}
    best = None
    for h in hits:
        lat, lon = float(h["lat"]), float(h["lon"])
        if not (HKI_BBOX[0] <= lat <= HKI_BBOX[1] and HKI_BBOX[2] <= lon <= HKI_BBOX[3]):
            continue
        if not _same_name(h.get("name") or "", name):
            continue                                     # "Kalasataman kirjasto" ≠ "Kalasatama"
        k = _kind(h)
        if k and (best is None or rank[k] < rank[best[2]]):
            best = (lat, lon, k)
    return best


def locate(cache, *texts, fallback=()):
    """(place, lat, lon, kind) — first candidate that geocodes, specific names first.
    `fallback` texts (e.g. the decision summary) are only consulted if `texts` fail,
    so a street merely mentioned in the summary never beats the title's own district."""
    for group in (texts, fallback):
        for name, _tier in candidates(*group):
            lat, lon, kind = geocode_name(name, cache)
            if lat is not None:
                return name, lat, lon, kind
    return None, None, None, "none"


def load_cache(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache, path):
    json.dump(cache, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
