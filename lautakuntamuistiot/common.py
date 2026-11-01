"""
Shared pieces: the plan-type classifier, decision-page parsing (heading, 'Päätös'
summary, plan-drawing PDF), a fetch helper and the default dataset paths.
"""
import urllib.request, re, json, html

from .settings import OUT, USER_AGENT

DATASET = f"{OUT}/plans_dataset.json"
GCACHE  = f"{OUT}/geocode_cache.json"

UA = {"User-Agent": USER_AGENT}
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
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
# whole-item hard exclude: clearly not a spatial plan (statements/reports/admin)
EXCLUDE = re.compile(r'oikaisuvaatimu|talousarvi|toimintasuunnitelma|maankäyttösopim|'
                     r'määrärah|virastopääll|hankinta|vuokra|kokousaj|'
                     r'lausunto|arviointi ja seuranta|seurantaraport|karvi|'
                     r'vastaus|kuntalaisaloit|aloitteeseen|tonttivaraus|tontinvaraus|varauksen jatka', re.I)


def classify(title_lc):
    for key, _label, _icon, match in TYPES:
        if match(title_lc):
            return key
    return None


# What the committee did with the plan. Committees approve street, park and most
# traffic plans themselves, but a zoning plan is only PROPOSED by the committee and
# approved later by the City Board or Council, so most zoning pins are proposals.
STAGES = {
    "approved": "approved by the committee",
    "proposal": "proposal or draft (approved later by the City Board / Council)",
    "returned": "returned for further preparation or tabled",
    "other":    "decision (stage not stated in the title or summary)",
    "consultation": "public consultation (Kerro kantasi), not a decision",
}
_RETURNED = re.compile(r'palaut\w* asian? uudelleen valmisteltavaksi|pöydälle', re.I)
_PROPOSAL = re.compile(r'\besity|\besittää|ehdotu|luonno|muistutu', re.I)
_APPROVED = re.compile(r'hyväksy', re.I)


def plan_stage(rec):
    """approved | proposal | returned | other — keyword heuristic over the title and
    heading first, then the 'Päätös' summary (see STAGES)."""
    head = f'{rec.get("title") or ""} {rec.get("heading") or ""}'
    summary = rec.get("summary") or ""
    if _RETURNED.search(summary):
        return "returned"
    for text in (head, summary):
        if _PROPOSAL.search(text):
            return "proposal"
        if _APPROVED.search(text):
            return "approved"
    return "other"


def better_decision(a, b):
    """True if record `a` should replace `b` for the same case on the map: the one with a
    plan drawing wins, otherwise the later decision; on a tie the record already kept
    stays. Used by build_kml's dedupe and by scrape_decisions."""
    def rank(r):
        d = (r.get("date") or "").split(".")
        day = int(d[0]) if len(d) == 3 and d[0].isdigit() else 0
        return bool(r.get("map_url")), r["year"], r["month"], day
    return rank(a) > rank(b)


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception:
        return ""


_pages = {}                     # decision-url -> html (fetched once)


def decision_page(url):
    # keep the ?paatos= query — the drawing attachment lives under the specific
    # decision; the asia base page often shows only the print-out.
    if url not in _pages:
        _pages[url] = fetch(url)
    return _pages[url]


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


def load_json(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default
