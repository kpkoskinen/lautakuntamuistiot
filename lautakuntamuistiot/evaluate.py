#!/usr/bin/env python3
"""
Measure the dataset's quality: automated checks plus a random sample for manual review.

Automated (offline, read-only):
  - counts per plan type, stage, committee and year
  - drawing coverage: share of decisions with a plan-drawing link, per type
  - geocode precision (street / place / district / manual) and pins outside Helsinki
  - duplicate (asia_id, plan_type, date) records and missing required fields

Optional (network, --check-drawings N): fetch the first bytes of N random drawing
links and check they really are PDFs (at most 1 request per second).

The sample CSV has one row per randomly chosen record with empty verdict columns
(type_ok, stage_ok, drawing_ok, location_ok, notes). Fill them in by opening the
decision and drawing links; the numbers here are not human-verified until someone does.

    python3 -m lautakuntamuistiot.evaluate                       # output/ dataset
    python3 -m lautakuntamuistiot.evaluate --dataset data/plans_dataset.json \\
        --sample 100 --seed 1 --csv output/quality_sample.csv
"""
import argparse, collections, csv, json, os, random, time, urllib.request

from .common import DATASET, STAGES, UA, plan_stage
from .locate import HKI_BBOX
from .settings import OUT

REQUIRED = ("asia_id", "plan_type", "title", "date", "decision_url", "lat", "lon")
VERDICTS = ("type_ok", "stage_ok", "drawing_ok", "location_ok", "notes")


def pct(n, d):
    return f"{n}/{d} ({100 * n / d:.0f}%)" if d else "0/0"


def table(title, counter, total=None):
    print(f"\n{title}")
    total = total or sum(counter.values())
    for k, n in sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0]))):
        print(f"  {str(k):<32} {n:>5}  {100 * n / total:5.1f}%")


def inside_helsinki(r):
    s, n, w, e = HKI_BBOX
    return s <= r["lat"] <= n and w <= r["lon"] <= e


def is_pdf(url):
    req = urllib.request.Request(url, headers=dict(UA, Range="bytes=0-7"))
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read(8).startswith(b"%PDF")
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(prog="python3 -m lautakuntamuistiot.evaluate",
                                 description="Measure the dataset's quality.")
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--sample", type=int, default=100, help="records in the review sample (0 = none)")
    ap.add_argument("--seed", type=int, default=1, help="random seed, so the sample is reproducible")
    ap.add_argument("--csv", default=f"{OUT}/quality_sample.csv", help="where to write the sample")
    ap.add_argument("--check-drawings", type=int, default=0, metavar="N",
                    help="fetch N random drawing links and check they are PDFs (network)")
    args = ap.parse_args()

    ds = json.load(open(args.dataset, encoding="utf-8"))
    recs = ds["records"]
    unlocated = ds.get("unlocated") or []
    for r in recs:
        r.setdefault("stage", plan_stage(r))
    print(f"{args.dataset}: {len(recs)} located records, {len(unlocated)} unlocated, "
          f"generated {ds.get('generated', '?')}")
    print(f"located share: {pct(len(recs), len(recs) + len(unlocated))}")

    table("plan type", collections.Counter(r["plan_type"] for r in recs))
    table("stage", collections.Counter(r["stage"] for r in recs))
    table("committee", collections.Counter(r.get("committee") for r in recs))
    table("year", collections.Counter(r.get("year") for r in recs))

    print("\ndrawing coverage (decisions linking a plan-drawing PDF)")
    by_type = collections.defaultdict(list)
    for r in recs:
        by_type[r["plan_type"]].append(r)
    for t, rs in by_type.items():
        print(f"  {t:<12} {pct(sum(1 for r in rs if r.get('map_url')), len(rs))}")
    print(f"  {'all':<12} {pct(sum(1 for r in recs if r.get('map_url')), len(recs))}")

    table("geocode precision", collections.Counter(r.get("geocode") for r in recs))
    outside = [r for r in recs if not inside_helsinki(r)]
    print(f"\npins outside the Helsinki bbox: {pct(len(outside), len(recs))}")
    for r in outside[:10]:
        print(f"  {r['asia_id']}  {r.get('location')}  ({r['lat']:.4f}, {r['lon']:.4f})")
    # (whether the pin is the RIGHT street can't be checked offline: the place name is
    # taken from the decision text, so only the manual review sample measures that)

    keys = collections.Counter((r["asia_id"], r["plan_type"], r.get("date")) for r in recs)
    print(f"duplicate (asia_id, plan_type, date): {sum(n - 1 for n in keys.values() if n > 1)}")
    for f in REQUIRED:
        missing = sum(1 for r in recs if r.get(f) in (None, ""))
        if missing:
            print(f"missing {f}: {missing}")

    rng = random.Random(args.seed)
    if args.check_drawings:
        pool = [r["map_url"] for r in recs if r.get("map_url")]
        urls = rng.sample(pool, min(args.check_drawings, len(pool)))
        ok = 0
        for u in urls:
            ok += is_pdf(u)
            time.sleep(1)
        print(f"\ndrawing links that are PDFs: {pct(ok, len(urls))}")

    if args.sample:
        sample = rng.sample(recs, min(args.sample, len(recs)))
        os.makedirs(os.path.dirname(os.path.abspath(args.csv)), exist_ok=True)
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["asia_id", "date", "committee", "plan_type", "stage", "title",
                        "location", "geocode", "osm", "decision_url", "map_url", *VERDICTS])
            for r in sample:
                osm = f"https://www.openstreetmap.org/?mlat={r['lat']}&mlon={r['lon']}#map=17/{r['lat']}/{r['lon']}"
                w.writerow([r["asia_id"], r.get("date"), r.get("committee"), r["plan_type"],
                            STAGES.get(r["stage"], r["stage"]), r.get("title"), r.get("location"),
                            r.get("geocode"), osm, r.get("decision_url"), r.get("map_url") or "",
                            *[""] * len(VERDICTS)])
        print(f"\nreview sample: {len(sample)} records -> {args.csv}")


if __name__ == "__main__":
    main()
