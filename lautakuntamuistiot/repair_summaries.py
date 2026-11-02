#!/usr/bin/env python3
"""
Re-read the summary of every paatokset.hel.fi decision already in the dataset.

A scrape doesn't correct records it already holds: the same decision never counts as
better than itself (common.better_decision). So after a change to the summary parser
or the stage heuristic, run this once. It updates only `summary` and `stage`;
locations, drawings and everything else stay as they are. The one exception is an
unlocated decision: `locate` also reads the summary, so it is located again and moves
onto the map if that now succeeds (unless its case is already on the map). A page that
fails to load or yields no summary keeps its summary, and re-running is safe.

    python3 -m lautakuntamuistiot.repair_summaries --dataset data/plans_dataset.json \
        --cache data/geocode_cache.json
"""
import argparse, collections, json, os, time

from .common import DATASET, GCACHE, decision_fields, fetch, load_json, plan_stage
from .locate import load_cache, locate, save_cache


def write_json(obj, path):
    """Write via a temp file, so an interrupted run never leaves a half-written dataset."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--cache", default=GCACHE, help="geocode cache, for unlocated decisions")
    ap.add_argument("--delay", type=float, default=0.7, help="seconds between page requests")
    args = ap.parse_args()

    ds = load_json(args.dataset, None)
    if ds is None:
        raise SystemExit(f"cannot read {args.dataset}")
    unlocated = ds.get("unlocated", [])
    recs = [r for r in ds["records"] + unlocated
            if "paatokset.hel.fi" in (r.get("decision_url") or "")]
    print(f"{len(recs)} decisions to re-read", flush=True)

    summaries = {}                 # decision url -> summary ('' if the page failed)
    changed, failed, no_summary = 0, 0, 0
    stages = collections.Counter()
    for i, r in enumerate(recs, 1):
        url = r["decision_url"]
        if url not in summaries:   # one case can be several records (plan types)
            page = fetch(url)
            time.sleep(args.delay)
            summaries[url] = (decision_fields(page)[1] or "") if page else None
        summary = summaries[url]
        if summary is None:
            failed += 1
            print(f"  ! could not open {url}", flush=True)
        elif not summary:
            no_summary += 1
        elif summary != r.get("summary"):
            r["summary"] = summary
            changed += 1
        # the stage heuristic may have changed too, so recompute it for every record
        stage = plan_stage(r)
        if stage != r.get("stage"):
            stages[f"{r.get('stage')} -> {stage}"] += 1
            r["stage"] = stage
        if i % 100 == 0:
            print(f"  {i}/{len(recs)}  ({changed} changed, {failed} failed)", flush=True)

    # unlocated decisions: the summary is locate's fallback, so try again
    cache = load_cache(args.cache)
    onmap = {(r["dm"], r["asia_id"], r["plan_type"]) for r in ds["records"]}
    still, moved = [], 0
    for r in unlocated:
        k = (r["dm"], r["asia_id"], r["plan_type"])
        loc, lat, lon, conf = (locate(cache, r.get("title"), r.get("heading"),
                                      fallback=(r.get("summary") or "",))
                               if k not in onmap else (None, None, None, "none"))
        if lat is None:
            still.append(r)
        else:
            ds["records"].append(dict(r, location=loc, lat=lat, lon=lon, geocode=conf))
            onmap.add(k)
            moved += 1
            print(f"  + located {loc} ({conf}): {r.get('heading')}", flush=True)
    ds["unlocated"] = still
    save_cache(cache, args.cache)

    print(f"{changed} summaries changed, {failed} pages failed, {no_summary} without a summary")
    print(f"stage changes: {dict(stages)}")
    print(f"{moved} unlocated decisions now located")
    if changed or stages or moved:
        ds["generated"] = time.strftime("%Y-%m-%d")
        write_json(ds, args.dataset)


if __name__ == "__main__":
    main()
