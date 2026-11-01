# Data — ready-made snapshot

> **Coming soon.** The first snapshot is being generated and will be added here. Until
> then, build your own with the tools (see the main [README](../README.md)).

This folder holds a snapshot of the scripts' output, so you can use the maps without
running a multi-hour scrape. Everything here can be regenerated with the scripts.

| file | what it is |
|------|------------|
| `plans_dataset.json` | Committee plan decisions, 2013 → snapshot date: heading, summary, date, plan type, location and links to the decision and the plan drawing. Plans that couldn't be located are in its `unlocated` list. |
| `kerrokantasi_dataset.json` | Plan-related Kerro kantasi public consultations, 2014 → snapshot date, with their drawings. |
| `helsinki_plans.kml` | The map built from both datasets with `python3 -m lautakuntamuistiot.build_kml`: one layer per plan type plus a consultation layer. Import it into Google My Maps or any GIS tool. |

The snapshot date is in each JSON's `generated` field. A snapshot does not update itself;
for newer decisions, re-run the scrapers.

## Caveats

This is **experimental, heuristically extracted data**, not an official dataset. Plan
detection, drawing choice and locations are all guessed, and pins are approximate and
can be wrong (see **Experimental tool** and **Location accuracy** in the main README).
Check against the linked hel.fi documents before relying on anything.

## Licence

The MIT licence of the code does **not** cover this data. It keeps its sources' licences:

- Decision, consultation and plan content: © City of Helsinki, **CC BY 4.0**. Credit the
  City of Helsinki.
- Coordinates geocoded with Nominatim: © OpenStreetMap contributors, **ODbL**.
