#!/usr/bin/env python3
"""
Enumerate plan decisions via the paatokset **Elasticsearch proxy** — the primary
source for everything from 2017 on, for u540 as well as its predecessors.

Endpoint discovered from the site's React decision-search:
    https://paatokset-elastic-proxy.api.hel.ninja/paatokset_decisions/_search
Each hit carries decision_url (full ?paatos= form), subject, organization_name,
field_policymaker_id, meeting_date (unix s), unique_issue_id (HEL-YYYY-NNNNNN).

We fetch EVERY decision of the committee (field_is_decision = true; the agenda-only
"a-asia" stubs with GUID ids are false and are followed by the real decision) and
classify the subject client-side with the same classifier as everywhere else. This
replaced a full-text pre-filter + the u540 meeting-page crawl, which together missed
~30% of plans (inflected plan words, non-hel- agenda links, silent geocode skips).

HARD LIMIT: the index only goes back to 2017 (verified: 0 decisions before
2017-01-01). 2013–2016 comes from scrape_decisions_2013.

For each plan we still open the decision page for the <h1> heading, the 'Päätös'
summary and the plan-drawing PDF, then locate it (locate, cached). Items that
can't be located are kept in the dataset's "unlocated" list rather than dropped.

    python3 -m lautakuntamuistiot.scrape_decisions --org "Kaupunkiympäristölautakunta"
    python3 -m lautakuntamuistiot.scrape_decisions --org "Yleisten töiden lautakunta"
    python3 -m lautakuntamuistiot.scrape_decisions --org "Kaupunkisuunnittelulautakunta"
"""
import urllib.request, json, re, argparse, time, os

from .common import classify, EXCLUDE, TYPES, decision_page, decision_fields, load_json, DATASET, GCACHE
from .locate import locate, save_cache
from .settings import USER_AGENT

ES = "https://paatokset-elastic-proxy.api.hel.ninja/paatokset_decisions/_search"
LABEL = {k: lbl for k, lbl, *_ in TYPES}
UA = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}


def es_query(body):
    req = urllib.request.Request(ES, data=json.dumps(body).encode(), headers=UA, method="POST")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


def all_decisions(org):
    """Every decision of a committee, oldest first (paged with search_after)."""
    out, after = [], None
    while True:
        body = {"size": 500, "sort": [{"meeting_date": "asc"}, {"id": "asc"}],
                "query": {"bool": {"filter": [{"term": {"organization_name": org}},
                                              {"term": {"field_is_decision": True}}]}},
                "_source": ["subject", "decision_url", "meeting_date",
                            "unique_issue_id", "field_policymaker_id"]}
        if after:
            body["search_after"] = after
        batch = es_query(body)["hits"]["hits"]
        if not batch:
            return out
        out += batch
        after = batch[-1]["sort"]


def one(v):
    return v[0] if isinstance(v, list) else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", required=True, help="organization_name, e.g. 'Kaupunkiympäristölautakunta'")
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--cache", default=GCACHE)
    args = ap.parse_args()

    ds = load_json(args.dataset, {"generated": None, "records": [], "unlocated": []})
    ds.setdefault("unlocated", [])
    cache = load_json(args.cache, {})
    bykey = {(r["dm"], r["asia_id"], r["plan_type"]): i for i, r in enumerate(ds["records"])}
    unloc = {(u["dm"], u["asia_id"], u["plan_type"]): u for u in ds["unlocated"]}

    print(f"[ES] all decisions for {args.org!r} ...", flush=True)
    hits = all_decisions(args.org)
    plans = []
    for h in hits:
        subject = one(h["_source"].get("subject")) or ""
        if EXCLUDE.search(subject):
            continue
        key = classify(subject.lower())
        if key:
            plans.append((h["_source"], subject, key))
    print(f"      {len(hits)} decisions -> {len(plans)} plan decisions", flush=True)

    added = updated = nloc = 0
    for i, (s, subject, key) in enumerate(plans, 1):
        dec = one(s.get("decision_url"))
        decision_url = "https://paatokset.hel.fi" + dec
        m = re.search(r'hel-\d{4}-\d+', dec, re.I)
        asia = (one(s.get("unique_issue_id")) or (m.group(0) if m else dec)).lower()
        dm = one(s.get("field_policymaker_id")) or args.org
        t = time.gmtime(one(s.get("meeting_date")))
        date = time.strftime("%d.%m.%Y", t)

        page = decision_page(decision_url)
        heading, summary, map_url = decision_fields(page) if page else (None, None, None)
        loc, lat, lon, conf = locate(cache, subject, heading, fallback=(summary,))
        k = (dm, asia, key)
        base = dict(committee=args.org, dm=dm, asia_id=asia, plan_type=key,
                    plan_type_label=LABEL[key], heading=heading or subject, title=subject,
                    summary=summary, date=date, year=t.tm_year, month=t.tm_mon,
                    decision_url=decision_url, map_url=map_url)
        if lat is None:
            unloc[k] = base; nloc += 1
        else:
            unloc.pop(k, None)
            rec = dict(base, location=loc, lat=lat, lon=lon, geocode=conf)
            if k in bykey:
                # several decisions per case (e.g. proposal, then approval): keep the
                # one with a plan drawing, else the later one (same rule as build_kml)
                old = ds["records"][bykey[k]]
                if rec["map_url"] or not old.get("map_url"):
                    ds["records"][bykey[k]] = rec; updated += 1
            else:
                bykey[k] = len(ds["records"]); ds["records"].append(rec); added += 1
        if i % 50 == 0:
            print(f"      {i}/{len(plans)}  (+{added} ~{updated} unlocated {nloc})", flush=True)
            save_cache(cache, args.cache)

    ds["unlocated"] = list(unloc.values())
    ds["generated"] = time.strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(args.dataset) or ".", exist_ok=True)
    json.dump(ds, open(args.dataset, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    save_cache(cache, args.cache)
    print(f"\n{args.org}: +{added} new, {updated} updated, {nloc} unlocated "
          f"-> dataset now {len(ds['records'])} records ({len(ds['unlocated'])} unlocated)")


if __name__ == "__main__":
    main()
