# lautakuntamuistiot — Helsinki city-plan maps

Scripts that collect the City of Helsinki's published **plan decisions and plan
drawings** — street, traffic, park and zoning plans, plus public consultations — and
turn them into **map layers (KML)** for Google My Maps or any GIS tool. Each pin links
the plan drawing (PDF) and the decision or consultation page it came from.

> ### ⚠️ Experimental tool
>
> This is an **experimental extraction tool, not an official or authoritative dataset**.
> Almost every step is **heuristic**:
>
> - **What counts as a plan** is decided by keyword patterns on decision titles
>   (*katusuunnitelma*, *asemakaava*, …). Some plans are missed and some unrelated
>   items get through.
> - **Which attachment is "the drawing"** is guessed from attachment names and captions.
>   It is usually right, but a pin can still link a location map, a report or a photo.
> - **Locations are approximate.** A place name is pulled from the title and geocoded
>   (OpenStreetMap / Nominatim). A pin marks *a point on the named street* or *a
>   district centre*, not the plan's real extent, and can be wrong. Overlapping pins are
>   spread apart on purpose, so the drawn position is further off by up to a few hundred metres.
> - **Sources are unofficial or undocumented.** It reads public web pages, an open
>   Elasticsearch proxy and static file folders, and these can change or vanish
>   without notice.
>
> Always check a pin against the linked decision or drawing before relying on it. The
> original documents on hel.fi are the source of truth.

## What you get

1. **Committee plan decisions, 2013 → now.** Decisions on street plans
   (*katusuunnitelma*), traffic (*liikennesuunnitelma*), park (*puistosuunnitelma*),
   zoning (*asemakaava*) and other plans, each with its drawing PDF. There is one
   colour-coded layer per type.
2. **Kerro kantasi consultations, 2014 → now.** Plan-related public hearings from
   kerrokantasi.hel.fi, with their drawings, as one more (purple) layer.
3. **Zoning archive, 1836 → now.** *Every valid zoning plan* in Helsinki from the city's
   open WFS, with real polygon geometry and the `kaavakartta` drawing. This is a separate
   product; see **Zoning archive** below.

## Requirements

- **Python 3.8+**, standard library only. There is nothing to `pip install`.
- **Network access** to hel.fi, paatokset.hel.fi, kerrokantasi.api.hel.fi, kartta.hel.fi,
  ptp.hel.fi, web.archive.org and nominatim.openstreetmap.org.
- **Time.** Geocoding follows Nominatim's usage policy (≤ 1 request/s, cached), so a
  first full scrape takes hours. Re-runs reuse the cache and are much faster.

## Quick start

```bash
# run from the repository directory
export LAUTAKUNTA_CONTACT="you@example.org"   # optional, identifies you to Nominatim
D=output/plans_dataset.json

# 1. scrape (network) — each step adds to the dataset; re-running is safe
python3 scrape_plans_es.py   --org "Kaupunkiympäristölautakunta"   --dataset $D   # 2017 →
python3 scrape_plans_es.py   --org "Kaupunkisuunnittelulautakunta" --dataset $D   # Jan–May 2017
python3 scrape_plans_es.py   --org "Yleisten töiden lautakunta"    --dataset $D   # Jan–May 2017
python3 scrape_plans_hela.py --committee ksv  --dataset $D                        # 2013 → 2017
python3 scrape_plans_hela.py --committee ytlk --dataset $D                        # 2013 → 2017
python3 scrape_kerrokantasi.py                                                    # consultations

# 2. render (no network) — pure function of the datasets
python3 build_kml.py --years 2013-2026 -o output/helsinki_plans.kml
```

Then import the `.kml` into Google My Maps (see below).

More render options:

```bash
python3 build_kml.py --years 2017-2026 --per-year   # one KML per year
python3 build_kml.py --years 2025                   # one year
python3 build_kml.py --min-sep 60                   # spread pins further apart
python3 build_kml.py --kerrokantasi ''              # without the consultation layer
python3 build_kml.py --no-dedupe                    # every decision as its own pin
```

### Where output goes

All output goes to **`output/`** inside the repository directory: datasets
(`*_dataset.json`), the geocoding cache (`geocode_cache.json`) and the maps (`*.kml`).
The directory is created on first run and is git-ignored, so **output is never
committed**. Only the scripts and this README live in the repo.

Two environment variables, read by `settings.py`, change the defaults:

| variable             | effect |
|----------------------|--------|
| `LAUTAKUNTA_OUT`     | output directory instead of `output/` |
| `LAUTAKUNTA_CONTACT` | an e-mail or URL appended to the User-Agent (`lautakuntamuistiot/1.0 (…)`). Nominatim's policy asks bulk users to identify themselves, so please set it for full scrapes. |

Most scripts also take `--dataset` / `-o` for a single run. Keep `geocode_cache.json`
if you plan to re-scrape, because it saves hours.

## Pipeline (JSON-first)

The scrape and the render are separate, with a reusable JSON dataset in between, so
you never have to re-scrape to re-render:

```
scrape_plans_es.py   ─┬─ paatokset ES proxy (u540 + predecessors, 2017→)
scrape_plans_hela.py ─┴─ hel.fi/static hela (predecessors 2013→2017) ─▶ plans_dataset.json ─┐
scrape_kerrokantasi.py ── kerrokantasi.api.hel.fi (2014→) ──────────▶ kerrokantasi_dataset.json ─┴▶ build_kml.py ─▶ *.kml
        │
        └── locate.py (title → validated place, + geocode_cache.json)
```

- **`scrape_plans_es.py`** is the main 2017→ scraper. It fetches **every** decision of a
  committee from the paatokset site's **Elasticsearch proxy**
  (`paatokset-elastic-proxy.api.hel.ninja/paatokset_decisions`, `field_is_decision=true`)
  and classifies the subject client-side, so nothing depends on a full-text pre-filter or
  on crawling meeting pages.
  - For each plan it opens the decision page for the **heading** (`<h1>`), the **summary**
    (*Päätös* text) and the plan-**drawing** PDF, then locates it with `locate.py`.
  - It upserts into `plans_dataset.json`, keyed on `dm + asia_id + plan_type`.
  - Plans that can't be located go to the dataset's `unlocated` list instead of vanishing.
  - Option: `--org "<organization_name>"`.
- **`locate.py`** maps a title to a place, using heuristics.
  - It extracts candidate names from the title:
    - street, park and square names in any inflection, restored to the nominative
      (*Caloniuksenkadun* → *Caloniuksenkatu*);
    - then district names: trailing title chunks and genitives like *Kalasataman* →
      *Kalasatama*.
  - It geocodes each candidate inside Helsinki and **accepts only an exact-name match of
    the right kind**: road → `street`, park/square → `place`, suburb/quarter → `district`.
    The city itself, transit stations and fuzzy POI matches are rejected.
  - Inflected words get several base-form guesses: consonant gradation *Viikin* → *Viikki*,
    *-ksen* → *-s*, *Östersundomin* → *Östersundom*.
  - Two-word street names (*Ida Aalbergin tie*, *Capellan puistotie*) are recognised.
  - A street that free-text search fuzzes to a neighbour (*Myllypadontie* →
    *Myllypurontie*) is retried as a structured `street=…&city=Helsinki` query.
  - Network failures are not cached as misses. `MANUAL` holds hand-fixed points.
- **`scrape_plans_hela.py`** reaches the predecessor committees for **2013→2017** from the
  live static decision repository `hel.fi/static/public/hela/`. paatokset only indexes
  2017+, and the OpenAhjo API and per-meeting ZIP bundles are dead.
  - Enumeration starts from the Internet Archive capture of the old meeting listing.
  - It then fetches each meeting's `Paatostiedote/.../index.html` and reads the agenda
    items and their named `Liite.pdf` attachments.
  - **Drawing choice.** Attachments come in agenda order, usually with the *Sijaintikartta*
    (location map) and *Ilmakuva* (aerial photo) first, so the drawing is picked **by name**
    (`best_drawing`), in this order:
    1. *Piirustus NNNN*, the zoning proposal's *…kartta*, *kaavarunko*, and street, traffic
       or park plan maps;
    2. other maps and plans;
    3. *havainnekuva*.
  - Location maps, aerial photos and reports (*selostus*, *vuorovaikutusraportti*,
    *selvitys*…) are never chosen as the drawing.
  - Every attachment is kept in the record (`attachments`) and listed on the pin.
  - Option: `--committee ksv|ytlk`. It writes `plans_pre2017_dataset.json` by default;
    pass `--dataset …/plans_dataset.json` to write straight into the main dataset.
- **`scrape_kerrokantasi.py`** collects public consultations from **Kerro kantasi**
  (`kerrokantasi.api.hel.fi/v1/hearing/`, open, 2014→).
  - It keeps the plan-related hearings (zoning, streets, parks, traffic) and drops schools,
    budgets and Q&A events.
  - It places each hearing at the centroid of its own drawn area (`geocode: "area"`). A
    hearing without an area is located with `locate.py`.
  - It lists the hearing's drawings: every PDF attachment plus every section image that
    isn't just a credited or stock photo.
  - Pins are labelled with the place name.
  - It writes `kerrokantasi_dataset.json`.
- **`build_kml.py`** renders pure output from the datasets, with no network.
  - **Slicing:** by year or year range and by committee, as one merged KML or one KML per
    year.
  - **Dedupe:** by default there is **one pin per `(asia_id, plan_type)`**. A plan decided
    across several meetings collapses to its best decision: the one with a drawing,
    otherwise the latest.
  - **Jan–May 2017 overlap:** these months exist in both hela and ES under different ids.
    The hela copy is dropped when an ES record has the same committee, date and type and a
    near-identical title.
  - **Pins never overlap.** Any pin within `--min-sep` metres (default 40) of an already
    placed one is moved out on a golden-angle spiral around its true point. More precise
    pins are placed first, so they stay put. Dataset coordinates are untouched, and a moved
    pin says "pin offset N m" in its description.
  - **Pin names** read `<place> – <plan type> MM/YYYY`.
  - **Kerro kantasi layer:** if `kerrokantasi_dataset.json` exists, it is added as a sixth
    layer, **Kerro kantasi (consultation)**, declustered together with the decisions.

Older helpers:
- `scrape_plans.py`, `list_meetings.py`, `build_year_map.py`, `build_plans_map.py` and
  `make_street_plans_map.py` are earlier per-meeting crawlers and builders.
  `scrape_plans_es.py`, `scrape_plans_hela.py` and `build_kml.py` still reuse their
  classifier, drawing-link extractor and dataset helpers.
- `check_locations.py` reverse-geocodes each pin to sanity-check locations.
- `settings.py` holds the output directory and User-Agent (see **Where output goes**).
- `bootstrap_dataset.py` is a one-off migration that built the first dataset from
  hand-verified per-year KMLs. It is kept for reference.

## `plans_dataset.json` record

```json
{
  "committee": "Kaupunkiympäristölautakunta", "dm": "u540",
  "asia_id": "hel-2024-013924",
  "plan_type": "katu", "plan_type_label": "Katusuunnitelma (street)",
  "heading": "Katusuunnitelma, Melkinlaiturin alue, Neptunuksenkatu 32179/1, …",
  "title":   "Neptunuksenkatu, Samoankuja, katusuunnitelmat, Länsisatama, Jätkäsaari",
  "summary": "Kaupunkiympäristölautakunta päätti hyväksyä seuraavat … katusuunnitelmat: …",
  "date": "28.01.2025", "year": 2025, "month": 1,
  "location": "Neptunuksenkatu", "lat": 60.1500909, "lon": 24.9069239,
  "geocode": "street",
  "decision_url": "https://paatokset.hel.fi/fi/asia/hel-2024-013924?paatos=…",
  "map_url": "https://ahjojulkaisu.hel.fi/5360EAE3-….pdf"
}
```

`plans_pre2017` (hela) records also carry `attachments: [[name, url], …]`. Kerro kantasi
records carry `drawings: [[label, url], …]` and `close_date`.

## Coverage

Committee plan decisions **2013 → now**, stitched from three sources:
- **Kaupunkiympäristölautakunta (`u540`) from Jun 2017, plus the predecessor committees'
  Jan–May 2017.** This is every decision in the paatokset Elasticsearch index
  (`scrape_plans_es.py`); that index starts in 2017. A meeting appears once its decisions
  are published, a few days after the meeting.
- **Predecessor committees, 2013→2017.** *Kaupunkisuunnittelulautakunta* (zoning/traffic)
  and *Yleisten töiden lautakunta* (street/park) come from the live `hela` repository
  (`scrape_plans_hela.py`). That is about 730 plan decisions, and 98.9 % of them have the
  plan drawing itself.

**2013 is a hard floor.** The committees' *live* päätöstiedote pages on
`hel.fi/static/public/hela/` exist from 2013 onwards; **2012 meeting folders are not
published live**. The other routes are closed too:
- The old meetings survive only inside the dead per-meeting ZIP bundles, and the Internet
  Archive captured those by name, not by content.
- The OpenAhjo API, which held the meeting→attachment mapping, was shut down in Dec 2024.
- Directory listing returns 403.
- The paatokset search index starts in 2017.

So committee drawings from 2012 and earlier can't be retrieved programmatically without a
bulk Ahjo export. Zoning drawings do go back to 1836, but through a different archive (next
section).

## Zoning archive (asemakaava) — 1836→

Helsinki publishes **every valid zoning plan** as open geodata, and every plan's drawing
PDF keyed on its plan number. That is 4 413 plans from 1836 to today, with real polygon
extents.

```
scrape_asemakaava.py  ─┬─ kartta.hel.fi WFS (plan index + geometry)  ─▶  asemakaava_dataset.json  ─▶  build_kaava_kml.py
                       └─ ptp.hel.fi (drawing + report PDFs, verified)
```

- **`scrape_asemakaava.py`** pulls the WFS layers
  `avoindata:Kaavahakemisto_alue_kaava_voimassa` (+ underground), one record per plan:
  `kaavatunnus`, acceptance date, district, polygon geometry + centroid, and the drawing
  and report PDF URLs.
  - It **verifies** each drawing by its magic bytes. The `ptp.hel.fi` handler always
    returns HTTP 200 and serves a 780-byte PNG placeholder when a plan has no PDF, so
    status codes can't be trusted.
  - Result: **4 404 / 4 413 (99.8 %)** have a real `kaavakartta` drawing.
  - Drawing: `https://ptp.hel.fi/DataHandlers/kaavapdf/?id=<kaavatunnus>`
  - Report: `https://ptp.hel.fi/DataHandlers/kaavaselostuspdf/?id=<kaavatunnus>`
- **`build_kaava_kml.py`** renders the archive **layered by era**:
  - `--points` (default) → `asemakaava_points.kml`: one centroid pin per plan, in 9 era
    layers (colour-graded old→new), each pin linking the real drawing PDF.
  - `--polygons --split` → `asemakaava_polygons_<era>.kml`: the real plan **extents**, one
    file per era. Each file can be imported as its own layer.

```bash
python3 scrape_asemakaava.py                  # pull + verify drawings (-> dataset)
python3 build_kaava_kml.py                    # asemakaava_points.kml
python3 build_kaava_kml.py --polygons --split # asemakaava_polygons_<era>.kml
```

## Import into Google My Maps

1. Go to <https://mymaps.google.com> → **Create a new map**.
2. **Import** → upload the `.kml`. The merged file has 6 layers, within My Maps' limits
   of 10 layers, 2 000 pins per layer and 10 000 in total.
3. Pins show the heading, the summary and clickable drawing and decision links.

A static KML does not update itself. To refresh, re-scrape, re-render and re-import.

## Location accuracy

Locations are **rough**, and each pin is tagged with its precision:

| tag        | meaning |
|------------|---------|
| `manual`   | hand-fixed in `locate.MANUAL` |
| `street`   | a point somewhere on the named street, not the plan's actual extent |
| `place`    | a named park, square or area |
| `area`     | centroid of a Kerro kantasi hearing's own drawn area |
| `district` | a neighbourhood centroid, used when nothing more specific in the title could be geocoded |

Many plans share a district centroid, which is why `build_kml.py` spreads overlapping
pins apart. `check_locations.py` reverse-geocodes pins to help spot wrong ones.

## Data sources and attribution

The scripts only read publicly available material. Respect each source's terms:

- **City of Helsinki** decisions, consultations and open geodata (paatokset.hel.fi,
  hel.fi, kerrokantasi.hel.fi, kartta.hel.fi). Open data is generally CC BY 4.0, so
  credit the City of Helsinki.
- **OpenStreetMap / Nominatim** for geocoding: © OpenStreetMap contributors, ODbL. Keep to
  the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)
  (≤ 1 request/s; the cache is there so you don't re-query).
- **Internet Archive** (web.archive.org), used only to enumerate 2013–2017 meetings.

The output maps link to the original documents. They do not copy them.
