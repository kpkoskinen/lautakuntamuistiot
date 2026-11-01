# Data — ready-made dataset

> **Updated daily.** A GitHub Action ([`update-data.yml`](../.github/workflows/update-data.yml),
> see **Automatic update** in the main README) adds new decisions and consultations here
> and commits when the data changed. On 1 Nov 2026 it held 1 727 located plan
> decisions (2013–2026, plus 105 unlocated), 185 Kerro kantasi consultations, 1 220 cached
> place names and a map with 1 807 pins. The [daily updated map on uMap](https://umap.openstreetmap.fr/en/map/kaupunkiymparistolautakunnan-suunnitelmat-ja-kaava_1479127) loads
> its pins from [`umap/`](umap/) here, so it always shows what is committed in this folder.

This folder holds the scripts' output, so you can use the maps without
running a multi-hour scrape. Everything here can be regenerated with the scripts.

| file | what it is |
|------|------------|
| `plans_dataset.json` | Committee plan decisions, 2013 → last update: heading, summary, date, plan type, location and links to the decision and the plan drawing. Each record's `stage` says whether the committee approved the plan or only proposed it (most zoning plans). Plans that couldn't be located are in its `unlocated` list. |
| `kerrokantasi_dataset.json` | Plan-related Kerro kantasi public consultations, 2014 → last update, with their drawings. |
| `geocode_cache.json` | Every place name looked up so far and its Nominatim result. The scrapers start from it, so a re-run doesn't repeat those lookups. |
| `update_log.md` | What each automatic update changed on the map (pins added, changed, removed), newest first. Written by `update_report`. |
| `quality_sample.csv` | 100 random decisions (`evaluate --seed 1`) with empty verdict columns for manual review. Not reviewed yet. |
| `helsinki_plans.umap` | The same map for [uMap](https://umap.openstreetmap.fr), built with `python3 -m lautakuntamuistiot.build_umap`: layers, colours, popups and a stage/year filter in one file. In uMap: **Import data** → this file → format **umap**. |
| `umap/*.geojson` | The same layers as plain GeoJSON, one file per plan type (`katu`, `liikenne`, `puisto`, `asemakaava`, `muu_k`, `kerrokantasi`). The example uMap map loads them from GitHub, so updating these files updates that map. |
| `helsinki_plans.kml` | The map built from both datasets with `python3 -m lautakuntamuistiot.build_kml`: one layer per plan type plus a consultation layer. Import it into Google My Maps or any GIS tool. |

The date of the last update is in each JSON's `generated` field (the git log shows when
the map last changed). `plans_dataset.json` also lists every processed decision URL in
`seen_decisions` (per committee), which the daily job uses to tell new decisions from
known ones. What each update changed is in [`update_log.md`](update_log.md).

## Caveats

This is **experimental, heuristically extracted data**, not an official dataset. Plan
detection, drawing choice and locations are all guessed, and pins are approximate and
can be wrong (see **Experimental tool** and **Location accuracy** in the main README).
Check against the linked hel.fi documents before relying on anything.

## Licence

The MIT licence of the code does **not** cover this data. It keeps its sources' terms
(details in the main README, **Data sources and licences**):

- **Decision titles and excerpts:** City of Helsinki decisions, not protected by
  copyright under section 9 of the Finnish Copyright Act (404/1961). Drawings and other
  attachments are only linked.
- **Consultation titles and abstracts:** from Kerro kantasi, whose terms publish its data
  under ODbL. The originals are linked.
- **Coordinates and `geocode_cache.json`:** geocoded with Nominatim, © OpenStreetMap
  contributors, **ODbL**.

This dataset is independent of the City of Helsinki. The original documents on hel.fi
are authoritative.
