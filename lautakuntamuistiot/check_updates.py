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

Prints what it found. In a GitHub Action it also writes `decisions`, `hearings` and
`pending` (each true|false) to $GITHUB_OUTPUT, so each later step runs only when there
is something for it, and the same text to the run's summary page. Exit
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
    out = []                                             # markdown, for the run summary

    ds = load_json(args.dataset, {"records": [], "unlocated": []})
    ds.setdefault("unlocated", [])
    plans = dec.plan_hits(dec.all_decisions(args.org))
    new, recheck = dec.pending(ds, plans, dec.seen_set(ds, args.org, plans, args.recheck_days),
                               args.recheck_days)
    drawn = [p for p in recheck if extract_pdf(decision_page(dec.decision_url(p[0])) or "")]
    out.append(f"**Decisions** ({args.org}): {len(new)} new, {len(drawn)} of {len(recheck)} "
               f"recent ones without a drawing now have one")
    for tag, (s, subject, _) in [("new", p) for p in new] + [("drawing", p) for p in drawn]:
        out.append(f"- {tag}: {time.strftime('%d.%m.%Y', time.gmtime(dec.meeting_ts(s)))} "
                   f"[{subject[:100]}]({dec.decision_url(s)})")

    kds = load_json(args.kerrokantasi, {"records": [], "unlocated": []})
    hnew, hopen = kk.pending(kds, kk.plan_hearings(kk.list_hearings()))
    out.append(f"\n**Kerro kantasi**: {len(hnew)} new, {len(hopen)} still open")
    for h in hnew:
        out.append(f"- new: {h['open_at'][:10]} [{kk.fi(h['title'])[:100]}]"
                   f"({kk.PAGE.format(h.get('slug') or h['id'])})")

    decisions, hearings = bool(new or drawn), bool(hnew)
    out.append("\n**Result:** " + ("new material, fetching it" if decisions or hearings
                                   else "nothing new"))
    print("\n".join(out))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"decisions={str(decisions).lower()}\nhearings={str(hearings).lower()}\n"
                    f"pending={str(decisions or hearings).lower()}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("## 1. Check\n\n" + "\n".join(out) + "\n\n")


if __name__ == "__main__":
    main()
