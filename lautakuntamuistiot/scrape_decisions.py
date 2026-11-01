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

Only new material (the scheduled job): the decision list is always fetched whole (a
few requests); --only-new then opens just the pending decisions (see pending()):
ones not seen before, plus recent ones still without a plan drawing, since
paatokset.hel.fi often attaches the drawing days or weeks after the meeting.
check_updates finds the same list, but opens only the recent no-drawing pages to see
whether a drawing has appeared.

    python3 -m lautakuntamuistiot.scrape_decisions --org "Kaupunkiympäristölautakunta" --only-new
    python3 -m lautakuntamuistiot.scrape_decisions --org "..." --since 2026-09-01

The dataset keeps every processed decision URL in `seen_decisions` (per committee), so a decision
that was opened but not kept (an earlier stage of a case whose later decision is on
the map) does not count as new again. A page that fails to load is retried on the next
runs and given up after 3 failures (`fetch_failures`), so a removed decision doesn't
count as new forever. The dataset is only rewritten when something in it changed.
"""
import urllib.request, json, re, argparse, time, os, calendar

from .common import (classify, plan_stage, better_decision, EXCLUDE, TYPES, decision_page,
                     decision_fields, load_json, DATASET, GCACHE)
from .locate import locate, load_cache, save_cache
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


def meeting_ts(s):
    return one(s.get("meeting_date")) or 0


def decision_url(s):
    return "https://paatokset.hel.fi" + one(s.get("decision_url"))


def plan_hits(hits):
    """[(source, subject, plan_type)] for the hits that are plan decisions."""
    plans = []
    for h in hits:
        subject = one(h["_source"].get("subject")) or ""
        if EXCLUDE.search(subject):
            continue
        key = classify(subject.lower())
        if key:
            plans.append((h["_source"], subject, key))
    return plans


def seen_set(ds, org, plans, margin_days=60):
    """Decision URLs of `org` already processed (`seen_decisions[org]`).

    A dataset from before seen_decisions existed has only the kept decisions, so the
    earlier-stage ones of a case would all look new. Bootstrap: the kept decision URLs,
    plus every plan decision from meetings more than `margin_days` before this org's
    latest kept decision. Decisions within that margin are opened once, which also
    catches ones the decision index published late."""
    by_org = ds.get("seen_decisions")
    if isinstance(by_org, dict) and org in by_org:
        return set(by_org[org])
    mine = [r for r in ds["records"] + ds.get("unlocated", []) if r.get("committee") == org]
    seen = {r.get("decision_url") for r in mine}
    dates = [calendar.timegm(time.strptime(r["date"], "%d.%m.%Y")) for r in mine if r.get("date")]
    if dates:
        cutoff = max(dates) - margin_days * 86400
        seen |= {decision_url(s) for s, _, _ in plans if meeting_ts(s) < cutoff}
    return seen


def pending(ds, plans, seen, recheck_days=60, now=None):
    """(new, recheck): plan decisions not in `seen`, and decisions from the last
    `recheck_days` days whose record still has no plan drawing."""
    no_drawing = {r.get("decision_url") for r in ds["records"] + ds.get("unlocated", [])
                  if not r.get("map_url")}
    cutoff = (now or time.time()) - recheck_days * 86400
    new = [p for p in plans if decision_url(p[0]) not in seen]
    recheck = [p for p in plans if decision_url(p[0]) in seen
               and decision_url(p[0]) in no_drawing and meeting_ts(p[0]) >= cutoff]
    return new, recheck


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org", required=True, help="organization_name, e.g. 'Kaupunkiympäristölautakunta'")
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--cache", default=GCACHE)
    ap.add_argument("--only-new", action="store_true",
                    help="open only pending decisions: new ones and recent ones without a drawing")
    ap.add_argument("--recheck-days", type=int, default=60,
                    help="with --only-new: how far back to re-check decisions without a drawing")
    ap.add_argument("--bootstrap-days", type=int, default=60,
                    help="for a dataset without seen_decisions: decisions from this many days "
                         "before the committee's newest record are opened once (see seen_set)")
    ap.add_argument("--since", default=None,
                    help="only open decisions from meetings on or after this date (YYYY-MM-DD)")
    args = ap.parse_args()

    ds = load_json(args.dataset, {"generated": None, "records": [], "unlocated": []})
    ds.setdefault("unlocated", [])
    cache = load_cache(args.cache)
    bykey = {(r["dm"], r["asia_id"], r["plan_type"]): i for i, r in enumerate(ds["records"])}
    unloc = {(u["dm"], u["asia_id"], u["plan_type"]): u for u in ds["unlocated"]}

    print(f"[ES] all decisions for {args.org!r} ...", flush=True)
    hits = all_decisions(args.org)
    plans = plan_hits(hits)
    print(f"      {len(hits)} decisions -> {len(plans)} plan decisions", flush=True)
    seen = seen_set(ds, args.org, plans, args.bootstrap_days)
    before = json.dumps(ds, sort_keys=True, ensure_ascii=False)
    fails = dict(ds.get("fetch_failures") or {})
    if args.only_new:
        new, recheck = pending(ds, plans, seen, args.recheck_days)
        plans = new + recheck
        print(f"      {len(new)} new, {len(recheck)} recent without a drawing to re-check", flush=True)
    if args.since:
        since_ts = calendar.timegm(time.strptime(args.since, "%Y-%m-%d"))
        plans = [p for p in plans if meeting_ts(p[0]) >= since_ts]
        print(f"      {len(plans)} from meetings on or after {args.since}", flush=True)
    plans.sort(key=lambda p: meeting_ts(p[0]))            # oldest first, as in a full run

    added = updated = nloc = 0
    for i, (s, subject, key) in enumerate(plans, 1):
        dec = one(s.get("decision_url"))
        url = decision_url(s)
        m = re.search(r'hel-\d{4}-\d+', dec, re.I)
        asia = (one(s.get("unique_issue_id")) or (m.group(0) if m else dec)).lower()
        dm = one(s.get("field_policymaker_id")) or args.org
        t = time.gmtime(meeting_ts(s))
        date = time.strftime("%d.%m.%Y", t)

        k = (dm, asia, key)
        page = decision_page(url)
        if page:
            seen.add(url); fails.pop(url, None)
        else:                          # retried on the next runs, given up after 3 failures
            fails[url] = fails.get(url, 0) + 1
            if fails[url] >= 3:
                seen.add(url)
            print(f"      ! could not open {url} (failure {fails[url]})", flush=True)
            if k in bykey or k in unloc:
                continue               # don't replace a known case with a title-only record
        heading, summary, map_url = decision_fields(page) if page else (None, None, None)
        loc, lat, lon, conf = locate(cache, subject, heading, fallback=(summary,))
        base = dict(committee=args.org, dm=dm, asia_id=asia, plan_type=key,
                    plan_type_label=LABEL[key], heading=heading or subject, title=subject,
                    summary=summary, date=date, year=t.tm_year, month=t.tm_mon,
                    decision_url=url, map_url=map_url)
        base["stage"] = plan_stage(base)
        if lat is None:
            # a case already on the map keeps its pin; else keep the better decision
            if k not in bykey and (k not in unloc or better_decision(base, unloc[k])):
                unloc[k] = base; nloc += 1
        else:
            unloc.pop(k, None)
            rec = dict(base, location=loc, lat=lat, lon=lon, geocode=conf)
            if k in bykey:
                # several decisions per case (e.g. proposal, then approval): keep the
                # one with a plan drawing, else the later one (common.better_decision,
                # also used by build_kml); by date, as --only-new may reopen an older one
                if better_decision(rec, ds["records"][bykey[k]]):
                    ds["records"][bykey[k]] = rec; updated += 1
            else:
                bykey[k] = len(ds["records"]); ds["records"].append(rec); added += 1
        if i % 50 == 0:
            print(f"      {i}/{len(plans)}  (+{added} ~{updated} unlocated {nloc})", flush=True)
            save_cache(cache, args.cache)

    ds["unlocated"] = list(unloc.values())
    if not isinstance(ds.get("seen_decisions"), dict):
        ds["seen_decisions"] = {}
    ds["seen_decisions"][args.org] = sorted(u for u in seen if u)
    ds.pop("fetch_failures", None)
    if fails:
        ds["fetch_failures"] = fails
    save_cache(cache, args.cache)
    if json.dumps(ds, sort_keys=True, ensure_ascii=False) == before and os.path.exists(args.dataset):
        print(f"\n{args.org}: nothing changed, dataset not rewritten")
        return
    ds["generated"] = time.strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(args.dataset) or ".", exist_ok=True)
    json.dump(ds, open(args.dataset, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n{args.org}: +{added} new, {updated} updated, {nloc} unlocated "
          f"-> dataset now {len(ds['records'])} records ({len(ds['unlocated'])} unlocated)")


if __name__ == "__main__":
    main()
