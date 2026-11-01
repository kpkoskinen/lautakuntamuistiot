#!/usr/bin/env python3
"""
Is there new material? Reads the two list endpoints (about 20 requests, no
geocoding) and compares them with the datasets:

  - committee decisions that are plans and haven't been processed yet,
  - recent decisions that had no plan drawing but now have one (it is often attached
    later; only these few decision pages are opened),
  - Kerro kantasi plan hearings not in the dataset yet.

    python3 -m lautakuntamuistiot.check_updates
    python3 -m lautakuntamuistiot.check_updates --org "Kaupunkiympäristölautakunta" --recheck-days 60

Prints what it found. In a GitHub Action it also writes `pending=true|false` to
$GITHUB_OUTPUT, so the later steps run only when there is something to fetch. Exit
code is 0 either way; a failing list request is an error (exit 1).

Hearings that are still open are refreshed by the scrape, but don't by themselves
count as new material.
"""
import argparse, os, time

from . import scrape_consultations as kk
from . import scrape_decisions as dec
from .common import DATASET, decision_page, extract_pdf, load_json


def main():
    ap = argparse.ArgumentParser(prog="python3 -m lautakuntamuistiot.check_updates")
    ap.add_argument("--org", default="Kaupunkiympäristölautakunta")
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--kerrokantasi", default=kk.DATASET)
    ap.add_argument("--recheck-days", type=int, default=60)
    args = ap.parse_args()

    ds = load_json(args.dataset, {"records": [], "unlocated": []})
    ds.setdefault("unlocated", [])
    new, recheck = dec.pending(ds, dec.plan_hits(dec.all_decisions(args.org)), args.recheck_days)
    drawn = [p for p in recheck if extract_pdf(decision_page(dec.decision_url(p[0])) or "")]
    print(f"decisions ({args.org}): {len(new)} new, {len(drawn)} of {len(recheck)} recent ones "
          f"without a drawing now have one")
    for s, subject, _ in new:
        print(f"  + {time.strftime('%d.%m.%Y', time.gmtime(dec.meeting_ts(s)))}  {subject[:100]}")

    kds = load_json(args.kerrokantasi, {"records": [], "unlocated": []})
    hnew, hopen = kk.pending(kds, kk.plan_hearings(kk.list_hearings()))
    print(f"Kerro kantasi: {len(hnew)} new, {len(hopen)} still open")
    for h in hnew:
        print(f"  + {h['open_at'][:10]}  {kk.fi(h['title'])[:100]}")

    found = bool(new or drawn or hnew)
    print("-> new material, run the scrape" if found else "-> nothing new")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"pending={'true' if found else 'false'}\n")


if __name__ == "__main__":
    main()
