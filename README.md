# lautakuntamuistiot — Helsinki city-plan maps

> **🗺️ [Daily updated map on uMap](https://umap.openstreetmap.fr/en/map/kaupunkiymparistolautakunnan-suunnitelmat-ja-kaava_1479190)** of Helsinki's committee plan decisions and
> Kerro kantasi consultations (OpenStreetMap, with stage and year filters).
>
> A GitHub Action checks every day for new decisions and consultations and adds them to
> [`data/`](data/) (see **Automatic update**); the map loads its pins from
> [`data/umap/`](data/umap/) each time it opens. For a map of your own, import
> [`data/helsinki_plans.umap`](data/helsinki_plans.umap) into
> [uMap](https://umap.openstreetmap.fr) (see **Show it on uMap**) or
> [`data/helsinki_plans.kml`](data/helsinki_plans.kml) into Google My Maps (see
> **Import into Google My Maps**).

Scripts that collect the City of Helsinki's published **plan decisions and plan
drawings** — street, traffic, park and zoning plans, plus public consultations — and
turn them into **map layers**: KML for Google My Maps or any GIS tool, and a `.umap`
file for [uMap](https://umap.openstreetmap.fr) on OpenStreetMap. Each pin links
the plan drawing (PDF) and the decision or consultation page it came from.

> **Helsingin suunnitelmapäätökset kartalla.** Työkalu kokoaa Helsingin lautakuntien
> katu-, liikenne-, puisto- ja asemakaavapäätökset (2013 →) sekä Kerro kantasi
> -kuulemiset kartalle. Jokainen merkintä linkittää alkuperäiseen päätökseen ja
> suunnitelmapiirustukseen. Sijainnit ja luokittelut on päätelty automaattisesti, joten
> tarkista tiedot aina alkuperäisestä asiakirjasta. Työkalu on riippumaton Helsingin
> kaupungista eikä ole kaupungin virallinen palvelu.
>
> *Helsinki's plan decisions on a map. An independent tool, not affiliated with the City
> of Helsinki.*

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

A ready-made dataset of 1 and 2 (JSON + KML) is in [`data/`](data/), and a daily GitHub
Action adds new decisions and consultations to it (see **Automatic update**). On 1 Nov
2026 it had 1 727 located plan decisions (2013–2026), 185 consultations and 1 807 map
pins. See [`data/README.md`](data/README.md). Use it if you don't want to run the scrape
yourself.

**To see it on a map,** import [`data/helsinki_plans.kml`](data/helsinki_plans.kml) into
your own Google My Maps (see **Import into Google My Maps**), or
[`data/helsinki_plans.umap`](data/helsinki_plans.umap) into uMap (see **Show it on uMap**).
Either takes a minute. The [daily updated map](https://umap.openstreetmap.fr/en/map/kaupunkiymparistolautakunnan-suunnitelmat-ja-kaava_1479190) at the top follows the data
in this repository.

### Example

One pin from the map, the street plan for Neptunuksenkatu in Jätkäsaari:

> **Neptunuksenkatu – katusuunnitelma 01/2025**<br>
> Katusuunnitelma, Melkinlaiturin alue, Neptunuksenkatu 32179/1, Samoankuja välillä
> Neptunuksenkatu-Tulimaankatu 30969/2, Länsisatama<br>
> Decision date: 28.01.2025 — approved by the committee<br>
> *Kaupunkiympäristölautakunta päätti hyväksyä seuraavat liitteenä olevat
> katusuunnitelmat: Neptunuksenkatu suunnitelmapiirustus nro 32179/1 (liite 2) …*<br>
> [Open plan drawing (PDF)](https://ahjojulkaisu.hel.fi/5360EAE3-D709-CD31-97FD-943F35D00000.pdf)<br>
> [Decision page](https://paatokset.hel.fi/fi/asia/hel-2024-013924?paatos=91410e3f-4598-cca5-a8bd-94f98c800006)<br>
> <small>Location: Neptunuksenkatu, approx: street-level</small>

### Decision or proposal?

Not every pin is an approved plan. Each record has a **`stage`**:

| stage          | meaning |
|----------------|---------|
| `approved`     | the committee approved the plan (street, park and most traffic plans) |
| `proposal`     | a proposal or draft: the committee sent it on, or put it on view. **Most zoning plans are here**, because the City Board or Council approves them, not the committee. |
| `returned`     | returned for further preparation, or tabled |
| `other`        | the title and summary don't say (mostly pre-2017 decisions without a summary) |
| `consultation` | a Kerro kantasi public consultation, not a decision |

The stage is a keyword heuristic (`common.plan_stage`) over the title and the *Päätös*
text, and the pin description shows it. Consultations have their own layer.

## Requirements

- **Python 3.8+**, standard library only. There is nothing to `pip install`.
- **Network access** to hel.fi, paatokset.hel.fi, kerrokantasi.api.hel.fi, kartta.hel.fi,
  ptp.hel.fi, web.archive.org and nominatim.openstreetmap.org.
- **Time.** Geocoding follows Nominatim's usage policy (≤ 1 request/s, cached). Re-runs
  reuse the cache and are much faster.

### Geocoding and Nominatim

The public Nominatim service is a shared, volunteer-run resource, and its
[usage policy](https://operations.osmfoundation.org/policies/nominatim/) discourages bulk
geocoding. So:

- **The cache is published.** [`data/geocode_cache.json`](data/) holds every place name
  the published data has looked up. A scrape whose own cache is empty starts from that file, so
  a full re-run only asks Nominatim about names that are not in it yet.
- **Identify yourself.** Set `LAUTAKUNTA_CONTACT` (below) before a full scrape.
- **Don't schedule full scrapes.** For regular updates, the policy limits scripts to
  4 requests per minute. Re-running one committee with a warm cache is fine; repeated
  cold full runs are not. The automatic update (below) only looks up names of new
  decisions and hearings, at most 4 per minute (`LAUTAKUNTA_GEOCODE_DELAY=15`). For heavier use, run your own Nominatim or use a commercial
  geocoder.

## Automatic update

[`.github/workflows/update-data.yml`](.github/workflows/update-data.yml) runs daily (and on
demand from the Actions tab) and updates the published data in `data/` in place
(`LAUTAKUNTA_OUT=data`), in three steps:

1. **Check.** `check_updates` reads the decision list and the Kerro kantasi hearing list
   and opens only a few pages: recent decisions that had no plan drawing, and hearings
   still open for comments. It reports plan decisions not processed yet, drawings that
   have appeared, new plan hearings and open hearings that changed. Usually under a
   minute; if there is nothing, the job stops here.
2. **Fetch only that.** `scrape_decisions --only-new` and `scrape_consultations --only-new`
   open and locate just the pending items and add them to the datasets; each runs only if
   its own source has something. New place names are looked up at most 4 per minute
   (`LAUTAKUNTA_GEOCODE_DELAY=15`). A dataset is rewritten only if something in it
   changed.
3. **Update.** `build_umap` and `build_kml` rebuild the maps. If anything in `data/`
   changed, `update_report` lists the pins added, changed and removed, and the job
   commits `data/` with that list as the commit message (or "datasets updated, map
   unchanged", e.g. for a decision that couldn't be located). The uMap map loads
   `data/umap/`, so it shows the new pins within minutes.

**What did the runs do?**

- **Every run:** the Actions tab → *Update data* lists all runs (kept 90 days). Each
  run's summary page shows what the check found (with links to the new decisions and
  hearings) and, if it fetched anything, what changed on the map.
- **Every update that changed something:** [`data/update_log.md`](data/update_log.md)
  (newest first) and the git log (`git log -- data`), both with the pins added and
  changed.
- A run that fails (for example a hel.fi site down) shows as failed in the Actions tab,
  and GitHub e-mails the repository owner by default.

The log lists the pins added, changed and removed, and below **Not on the map** what
the update did that doesn't show as a pin: decisions checked but not shown (an earlier
stage of a case already on the map), items that couldn't be located, pages that failed
to load.

GitHub pauses scheduled workflows after 60 days without repository activity (runs don't
count), and summer breaks have had up to 70 days without new decisions or consultations
(2019; 61 days in 2023). So each scheduled run ends with a **Keepalive** step that
re-enables the workflow through the API, which resets the timer without a commit.

Set the repository variable `LAUTAKUNTA_CONTACT` (Settings → Secrets and variables →
Actions → Variables) to identify the job to Nominatim. The same steps work locally on
the committed data (they update `data/` in place, as the job does):

```bash
export LAUTAKUNTA_OUT=data LAUTAKUNTA_GEOCODE_DELAY=15
python3 -m lautakuntamuistiot.check_updates
python3 -m lautakuntamuistiot.scrape_decisions --org "Kaupunkiympäristölautakunta" --only-new
python3 -m lautakuntamuistiot.scrape_consultations --only-new
python3 -m lautakuntamuistiot.build_umap -o data/helsinki_plans.umap
python3 -m lautakuntamuistiot.build_kml -o data/helsinki_plans.kml
python3 -m lautakuntamuistiot.update_report        # what changed, compared with the last commit
```

Without `LAUTAKUNTA_OUT=data` they work on `output/`; `--only-new` on an empty
`output/` would treat every decision as new, which is a full scrape.

`plans_dataset.json` keeps every processed decision URL in `seen_decisions` (per
committee), so an earlier-stage decision that isn't on the map doesn't count as new
again. Of the several decisions of one case, the map keeps the one with a plan drawing,
else the latest. A dataset from before `seen_decisions` existed is bootstrapped from its
records, and decisions from the last 60 days before its newest record
(`--bootstrap-days`) are opened once. A decision page that fails to load is retried on
the following runs and given up after 3 failures (`fetch_failures`). Closed
hearings already in the dataset are not re-read (the hearing list has no "modified"
date); a full `scrape_consultations` run refreshes them all.

## Quick start

```bash
# run from the repository root
export LAUTAKUNTA_CONTACT="you@example.org"   # optional, identifies you to Nominatim
D=output/plans_dataset.json

# 1. scrape (network) — each step adds to the dataset; re-running is safe
python3 -m lautakuntamuistiot.scrape_decisions      --org "Kaupunkiympäristölautakunta"   --dataset $D  # 2017 →
python3 -m lautakuntamuistiot.scrape_decisions      --org "Kaupunkisuunnittelulautakunta" --dataset $D  # Jan–May 2017
python3 -m lautakuntamuistiot.scrape_decisions      --org "Yleisten töiden lautakunta"    --dataset $D  # Jan–May 2017
python3 -m lautakuntamuistiot.scrape_decisions_2013 --committee ksv  --dataset $D                       # 2013 → 2017
python3 -m lautakuntamuistiot.scrape_decisions_2013 --committee ytlk --dataset $D                       # 2013 → 2017
python3 -m lautakuntamuistiot.scrape_consultations                                                      # consultations

# 2. render (no network) — pure function of the datasets
python3 -m lautakuntamuistiot.build_kml --years 2013-2026 -o output/helsinki_plans.kml
python3 -m lautakuntamuistiot.build_umap -o output/helsinki_plans.umap   # same map for uMap (+ output/umap/*.geojson)
```

Then import the `.kml` into Google My Maps or the `.umap` into uMap (see below).

More render options:

```bash
python3 -m lautakuntamuistiot.build_kml --years 2017-2026 --per-year   # one KML per year
python3 -m lautakuntamuistiot.build_kml --years 2025                   # one year
python3 -m lautakuntamuistiot.build_kml --min-sep 60                   # spread pins further apart
python3 -m lautakuntamuistiot.build_kml --kerrokantasi ''              # without the consultation layer
python3 -m lautakuntamuistiot.build_kml --no-dedupe                    # every decision as its own pin
```

### Where output goes

All output goes to **`output/`** in the repository root: datasets
(`*_dataset.json`), the geocoding cache (`geocode_cache.json`) and the maps (`*.kml`,
`*.umap` and `umap/*.geojson`).
The directory is created on first run and is git-ignored. The published data in
[`data/`](data/) is the only data kept in the repo.

Two environment variables, read by `lautakuntamuistiot/settings.py`, change the defaults:

| variable             | effect |
|----------------------|--------|
| `LAUTAKUNTA_OUT`     | output directory instead of `output/` |
| `LAUTAKUNTA_CONTACT` | an e-mail or URL appended to the User-Agent (`lautakuntamuistiot/1.0 (…)`). Nominatim's policy asks bulk users to identify themselves, so please set it for full scrapes. |
| `LAUTAKUNTA_GEOCODE_DELAY` | seconds between Nominatim requests (default 1.1, i.e. at most 1 per second). The scheduled job uses 15, i.e. at most 4 per minute. |

Most tools also take `--dataset` / `-o` for a single run. Keep `geocode_cache.json`
if you plan to re-scrape, because it saves hours.

## Repository layout

```
README.md  LICENSE
data/                         published data, updated daily (JSON, KML, .umap + umap/*.geojson), see data/README.md
lautakuntamuistiot/           the Python package; run each tool with python3 -m
├── settings.py               output directory and User-Agent
├── common.py                 plan-type classifier, decision-page parsing, fetch helper
├── locate.py                 title → validated place (Nominatim, cached)
├── scrape_decisions.py       committee decisions 2017 →     (paatokset ES proxy)
├── scrape_decisions_2013.py  committee decisions 2013–2017  (hel.fi static hela)
├── scrape_consultations.py   Kerro kantasi consultations    (kerrokantasi API)
├── check_updates.py          is there new material? (lists only, for the daily job)
├── update_report.py          what an update changed on the map (summary + update log)
├── scrape_zoning.py          zoning archive 1836 →          (kartta.hel.fi WFS)
├── build_kml.py              decisions + consultations → KML
├── build_umap.py             decisions + consultations → uMap (.umap)
├── build_zoning_kml.py       zoning archive → KML
├── evaluate.py               quality metrics + random sample for manual review
└── check_locations.py        reverse-geocode pins to spot wrong locations
```

## Pipeline (JSON-first)

The scrape and the render are separate, with a reusable JSON dataset in between, so
you never have to re-scrape to re-render:

```
scrape_decisions      ─┬─ paatokset ES proxy (u540 + predecessors, 2017→)
scrape_decisions_2013 ─┴─ hel.fi/static hela (predecessors 2013→2017) ─▶ plans_dataset.json ─┐
scrape_consultations  ── kerrokantasi.api.hel.fi (2014→) ──────────▶ kerrokantasi_dataset.json ─┴▶ build_kml ─▶ *.kml
        │
        └── locate (title → validated place, + geocode_cache.json)
```

- **`scrape_decisions`** is the main 2017→ scraper. It fetches **every** decision of a
  committee from the paatokset site's **Elasticsearch proxy**
  (`paatokset-elastic-proxy.api.hel.ninja/paatokset_decisions`, `field_is_decision=true`)
  and classifies the subject client-side, so nothing depends on a full-text pre-filter or
  on crawling meeting pages.
  - For each plan it opens the decision page for the **heading** (`<h1>`), the **summary**
    (*Päätös* text) and the plan-**drawing** PDF, then locates it with `locate`.
  - It upserts into `plans_dataset.json`, keyed on `dm + asia_id + plan_type`.
  - Plans that can't be located go to the dataset's `unlocated` list instead of vanishing.
  - Every processed decision URL is kept in `seen_decisions`, per committee.
  - Options: `--org "<organization_name>"`; `--only-new` opens only decisions not in
    `seen_decisions` plus recent ones still without a drawing (`--recheck-days`, default
    60); `--since YYYY-MM-DD` limits it to meetings from that date; `--bootstrap-days`
    (default 60) is only used for a dataset that has no `seen_decisions` yet.
- **`locate`** maps a title to a place, using heuristics.
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
- **`scrape_decisions_2013`** reaches the predecessor committees for **2013→2017** from the
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
- **`scrape_consultations`** collects public consultations from **Kerro kantasi**
  (`kerrokantasi.api.hel.fi/v1/hearing/`, open, 2014→).
  - It keeps the plan-related hearings (zoning, streets, parks, traffic) and drops schools,
    budgets and Q&A events.
  - It places each hearing at the centroid of its own drawn area (`geocode: "area"`). A
    hearing without an area is located with `locate`.
  - It lists the hearing's drawings: every PDF attachment plus every section image that
    isn't just a credited or stock photo.
  - Pins are labelled with the place name.
  - It writes `kerrokantasi_dataset.json`. With `--only-new` it keeps the dataset and opens
    only hearings not in it yet plus the ones still open for comments, and rewrites it
    only if something changed.
- **`check_updates`** tells whether there is new material, for the daily job: it reads
  the decision and hearing lists, and opens just the pages of recent decisions that had
  no drawing and of hearings still open for comments. It prints what it found, writes `decisions`, `hearings` and `pending`
  (true|false) to `$GITHUB_OUTPUT` and the same text to the run's summary page.
- **`update_report`** compares the layers in `data/umap/` with the last commit and lists
  the pins added, changed and removed (pins only nudged aside, less than 150 m, for a
  new neighbour are just counted), then compares the datasets for what doesn't show on
  the map: decisions checked but not shown, unlocated items, failed pages. With `--log FILE` it adds the list to the top of `data/update_log.md`.
- **`build_kml`** renders pure output from the datasets, with no network.
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

Shared pieces:
- **`common`** holds what the scrapers and `build_kml` share: the plan-type classifier
  (`TYPES`, `EXCLUDE`), the stage heuristic (`plan_stage`), the decision-page parser (heading, *Päätös* summary, drawing PDF)
  and the default dataset paths.
- **`check_locations`** reverse-geocodes each pin to sanity-check locations.
- **`settings`** holds the output directory and User-Agent (see **Where output goes**).

## `plans_dataset.json` record

```json
{
  "committee": "Kaupunkiympäristölautakunta", "dm": "U540",
  "asia_id": "hel-2024-013924",
  "plan_type": "katu", "plan_type_label": "Katusuunnitelma (street)", "stage": "approved",
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
  (`scrape_decisions`); that index starts in 2017. A meeting appears once its decisions
  are published, a few days after the meeting.
- **Predecessor committees, 2013→2017.** *Kaupunkisuunnittelulautakunta* (zoning/traffic)
  and *Yleisten töiden lautakunta* (street/park) come from the live `hela` repository
  (`scrape_decisions_2013`). That is about 730 plan decisions, and 98.9 % of them have the
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
scrape_zoning  ─┬─ kartta.hel.fi WFS (plan index + geometry)  ─▶  asemakaava_dataset.json  ─▶  build_zoning_kml
                └─ ptp.hel.fi (drawing + report PDFs, verified)
```

- **`scrape_zoning`** pulls the WFS layers
  `avoindata:Kaavahakemisto_alue_kaava_voimassa` (+ underground), one record per plan:
  `kaavatunnus`, acceptance date, district, polygon geometry + centroid, and the drawing
  and report PDF URLs.
  - It **verifies** each drawing by its magic bytes. The `ptp.hel.fi` handler always
    returns HTTP 200 and serves a 780-byte PNG placeholder when a plan has no PDF, so
    status codes can't be trusted.
  - Result: **4 404 / 4 413 (99.8 %)** have a real `kaavakartta` drawing.
  - Drawing: `https://ptp.hel.fi/DataHandlers/kaavapdf/?id=<kaavatunnus>`
  - Report: `https://ptp.hel.fi/DataHandlers/kaavaselostuspdf/?id=<kaavatunnus>`
- **`build_zoning_kml`** renders the archive **layered by era**:
  - `--points` (default) → `asemakaava_points.kml`: one centroid pin per plan, in 9 era
    layers (colour-graded old→new), each pin linking the real drawing PDF.
  - `--polygons --split` → `asemakaava_polygons_<era>.kml`: the real plan **extents**, one
    file per era. Each file can be imported as its own layer.

```bash
python3 -m lautakuntamuistiot.scrape_zoning                         # pull + verify drawings (-> dataset)
python3 -m lautakuntamuistiot.build_zoning_kml                      # asemakaava_points.kml
python3 -m lautakuntamuistiot.build_zoning_kml --polygons --split   # asemakaava_polygons_<era>.kml
```

## Import into Google My Maps

1. Download [`data/helsinki_plans.kml`](data/helsinki_plans.kml) (or build your own).
2. Go to <https://mymaps.google.com> → **Create a new map**.
3. In the first layer, click **Import** and upload the `.kml`. The file has 6 layers,
   within My Maps' limits of 10 layers, 2 000 pins per layer and 10 000 in total.
4. Pins show the heading, the summary and clickable drawing and decision links.

A static KML does not update itself. To refresh, re-scrape, re-render and re-import.

## Show it on uMap

[uMap](https://umap.openstreetmap.fr) draws on OpenStreetMap and imports its own `.umap`
format in one step: layers, colours, popups and filters. Use that file rather than the
KML: uMap imports KML too, but only as data, without uMap's layer, popup and filter
settings, and the popups are KML HTML rather than uMap's own text format.

1. Go to <https://umap.openstreetmap.fr> → **Create a map**. To edit the map later, log
   in first; an anonymous map is editable only through its secret edit link.
2. Click **Import data** (the arrow-up icon on the right), choose
   [`data/helsinki_plans.umap`](data/helsinki_plans.umap) (or your own `build_umap`
   output), check that the format says **umap**, and click **Import data** again.
3. Click **Save**, then share the map through **Share and download** (link or embed code).

You get 6 layers in the KML's colours, a **Stage** and **Year** filter, and popups with the
heading, decision date and stage, summary, drawing and decision links and location
accuracy. Each pin also keeps the plain fields (`date`, `year`, `stage`, `plan_type`,
`location`, `geocode`, `drawing_url`, `decision_url`, ...), so the table view and custom
popup templates can use them.

A map made this way does not update itself: to refresh it, delete the layers and import
a new file.

### A uMap map that follows the repository

`build_umap` also writes each layer as plain GeoJSON to a `umap/` folder next to its
output (`katu.geojson`, `liikenne.geojson`, ...; the published ones are in
[`data/umap/`](data/umap/)), plus `all.geojson` with every plan type in one file. A uMap layer can load such a file from a URL each time the
map opens, so a map pointing at the files on GitHub shows whatever was last committed —
no re-import. The [daily updated map on uMap](https://umap.openstreetmap.fr/en/map/kaupunkiymparistolautakunnan-suunnitelmat-ja-kaava_1479190) works this way: one
clustered layer per plan type, each loading its `data/umap/<type>.geojson` on `main`
([`data/helsinki_plans_clustered.umap`](data/helsinki_plans_clustered.umap)).

**Clustered per plan type (`--cluster-per-type`)** — the live map. Each plan type is
its own layer of uMap's *Clustered* type, so pins of one type merge into a numbered
circle in that type's colour; clicking it zooms in. The per-type files are already
spread (`--min-sep`, 40 m), so no two pins share a spot and no fan is needed: a pile
splits into single pins at about zoom 17 (40 m ≈ 67 px there; uMap clusters pins closer
than 60 px). Moved pins are typically about 55 m and at most about 160 m off their
point, and say so in the popup. Hovering a pin shows date, heading and the start of
the summary; the layers toggle the plan types, stage and year are filters.

```sh
python3 -m lautakuntamuistiot.build_umap --cluster-per-type --remote-base \
    https://raw.githubusercontent.com/OWNER/REPO/main/data/umap -o output/live.umap
```

**One clustered layer (`--combined`).** All plan types in one layer of uMap's *Clustered*
type, so overlapping pins of any type merge into one numbered circle. Clicking it zooms
in; where several plans share one spot (e.g. all plans geocoded to the same street),
clicking it again fans them out to choose from. Pins stay at their true points (no
spreading), keep their plan type's colour, and show date, heading and the start of the
summary on hover. Plan type, stage and year are filters.

```sh
python3 -m lautakuntamuistiot.build_umap --combined --remote-base \
    https://raw.githubusercontent.com/OWNER/REPO/main/data/umap -o output/live.umap
```

A click on the map closes an open fan, popup included (uMap's behaviour; close a popup
with × to keep the fan).

For plain (unclustered) layers per plan type instead, build a `.umap` whose layers point at the files
instead of carrying the data, and import it as above:

```sh
python3 -m lautakuntamuistiot.build_umap --remote-base \
    https://raw.githubusercontent.com/OWNER/REPO/main/data/umap -o output/live.umap
```

(Or, in an existing map, set each layer's **Remote data**: the file's raw URL, format
**geojson**.) Then updating the map is: re-run the scrapers, rebuild into `data/`, commit
and push. In this repository the daily Action does that (see **Automatic update**). GitHub caches raw files for about 5 minutes. The layer names leave out the pin
counts, since those would go stale.

Both kinds of file use a grey background (Jawg Light) so the coloured pins stand out; pick
another with the **Change tilelayers** button in edit mode, if you like.

Credit the data as in **Data sources and licences**: the file sets a short credit
line, but check it in the map's settings under **Credits**.

## Measuring quality

`evaluate` prints automated checks and draws a random sample for manual review:

```bash
python3 -m lautakuntamuistiot.evaluate --dataset data/plans_dataset.json \
    --sample 100 --seed 1 --csv output/quality_sample.csv [--check-drawings 50]
```

- **Automated:**
  - counts by type, stage, committee and year;
  - drawing coverage per type;
  - geocode precision;
  - pins outside Helsinki;
  - duplicates and missing fields.
  - `--check-drawings N` fetches N random drawing links and checks they are real PDFs.
- **Manual:** the CSV lists 100 random records with links to the decision, the drawing
  and the pin on OpenStreetMap, plus empty `type_ok`, `stage_ok`, `drawing_ok` and
  `location_ok` columns. Accuracy is only known once someone has filled them in.
  The automated checks can't tell whether a pin is on the *right* street, because the
  place name itself comes from the decision text.

On the data of 1 Nov 2026:

| check | result |
|-------|--------|
| decisions located | 1 727 / 1 832 (94 %); the rest are in `unlocated` |
| decisions linking a drawing | 1 581 / 1 727 (92 %): katu 94 %, puisto 92 %, asemakaava 92 %, liikenne 90 %, muu kaava 81 % |
| random drawing links that are real PDFs | 30 / 30 |
| geocode precision | street 68 %, district 25 %, place 6 %, manual 0.3 % |
| pins outside Helsinki / duplicates | 0 / 0 |
| stage | proposal 48 %, approved 41 %, other 10 %, returned 0.7 % |

The 100-record review sheet is [`data/quality_sample.csv`](data/quality_sample.csv)
(seed 1). **It has not been reviewed yet**, so plan-type, drawing and location accuracy
are still unmeasured.

## Location accuracy

Locations are **rough**, and each pin is tagged with its precision:

| tag        | meaning |
|------------|---------|
| `manual`   | hand-fixed in `locate.MANUAL` |
| `street`   | a point somewhere on the named street, not the plan's actual extent |
| `place`    | a named park, square or area |
| `area`     | centroid of a Kerro kantasi hearing's own drawn area |
| `district` | a neighbourhood centroid, used when nothing more specific in the title could be geocoded |

Many plans share a district centroid, which is why `build_kml` spreads overlapping
pins apart. `check_locations` reverse-geocodes pins to help spot wrong ones.

## Data sources and licences

The scripts only read publicly available material. What the datasets contain, and on what
terms:

- **Committee decisions** (paatokset.hel.fi; pre-2017 bulletins on hel.fi). Titles and
  short excerpts of the decision text are included. Decisions and statements of
  authorities are **not protected by copyright** under section 9 of the Finnish Copyright
  Act ([404/1961](https://www.finlex.fi/fi/laki/ajantasa/1961/19610404)). Independent
  works attached to them, such as plan drawings, reports and photos, may be, so they are
  **linked, not copied**.
- **Kerro kantasi consultations** (kerrokantasi.hel.fi). Only titles, short abstracts and
  links are included. The service's
  [terms](https://github.com/City-of-Helsinki/kerrokantasi-ui/blob/main/cities/helsinki/i18n/service-info/content.en.md)
  publish its data under **ODbL** and user comments under CC BY-NC-SA 4.0; no comments
  are collected. Treat the abstracts as the City's material and link back to the original.
- **Zoning archive** (kartta.hel.fi WFS,
  [HRI](https://hri.fi/data/fi/dataset/helsingin-asemakaavahakemistokartta-asemakaavahakemisto)):
  **CC BY 4.0**. Credit: "Data ja kartat (c) Helsingin kaupunki, kaupunkimittauspalvelut".
  Zoning drawings on ptp.hel.fi are linked only.
- **Coordinates** from Nominatim: © OpenStreetMap contributors,
  [ODbL](https://www.openstreetmap.org/copyright).
- **Internet Archive** (web.archive.org), used only to list the 2013–2017 meetings.

The original documents on hel.fi are authoritative. This project is independent of the
City of Helsinki.

## Licence

The code is released under the [MIT License](LICENSE). The data it collects keeps its
sources' terms (see **Data sources and licences** above); MIT does not cover it.
