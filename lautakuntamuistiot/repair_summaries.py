#!/usr/bin/env python3
"""
Re-read the summary of every paatokset.hel.fi decision already in the dataset.

A scrape doesn't correct records it already holds: the same decision never counts as
better than itself (common.better_decision). So after a change to the summary parser,
run this once. It updates only `summary` and `stage`; locations, drawings and
everything else stay as they are. A page that fails to load or yields no summary
leaves its record untouched, and re-running is safe.

    python3 -m lautakuntamuistiot.repair_summaries --dataset data/plans_dataset.json
"""
import argparse, collections, json, time

from .common import DATASET, decision_fields, decision_page, load_json, plan_stage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--delay", type=float, default=0.7, help="seconds between page requests")
    args = ap.parse_args()

    ds = load_json(args.dataset, None)
    if ds is None:
        raise SystemExit(f"cannot read {args.dataset}")
    recs = [r for r in ds["records"] + ds.get("unlocated", [])
            if "paatokset.hel.fi" in (r.get("decision_url") or "")]
    print(f"{len(recs)} decisions to re-read", flush=True)

    changed, failed, no_summary = 0, 0, 0
    stages = collections.Counter()
    for i, r in enumerate(recs, 1):
        page = decision_page(r["decision_url"])
        time.sleep(args.delay)
        if not page:
            failed += 1
            print(f"  ! could not open {r['decision_url']}", flush=True)
            continue
        summary = decision_fields(page)[1]
        if not summary:
            no_summary += 1
        elif summary != r.get("summary"):
            r["summary"] = summary
            stage = plan_stage(r)
            if stage != r.get("stage"):
                stages[f"{r.get('stage')} -> {stage}"] += 1
                r["stage"] = stage
            changed += 1
        if i % 100 == 0:
            print(f"  {i}/{len(recs)}  ({changed} changed, {failed} failed)", flush=True)

    print(f"{changed} summaries changed, {failed} pages failed, {no_summary} without a summary")
    print(f"stage changes: {dict(stages)}")
    if changed:
        ds["generated"] = time.strftime("%Y-%m-%d")
        with open(args.dataset, "w", encoding="utf-8") as f:
            json.dump(ds, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
