#!/usr/bin/env python3
"""
Step 1 of the street-plan map: list a committee's meetings for a year — no API.

paatokset.hel.fi has no public API and its search is JS-only, BUT each meeting
document is server-rendered at a predictable URL:

    https://paatokset.hel.fi/fi/paattajat/<dm>/asiakirjat/<DM><YEAR><n>

where <DM> is the decision-maker id (U540 = Kaupunkiympäristölautakunta), <YEAR>
is 4 digits, and <n> is a running meeting counter (1..~40/yr). We probe n=1..MAX,
keep the 200s, and read the meeting number + date from the page <title>. 404 past
the last meeting.

Output: a JSON list of meetings -> output/ (never committed). Sanity-check it before
running the decision enumerator (step 2).

    python3 list_meetings.py --year 2025
    python3 list_meetings.py --year 2025 -o meetings_2025.json
"""
import urllib.request, re, json, argparse, sys, time

from settings import OUT, USER_AGENT

BASE = "https://paatokset.hel.fi/fi/paattajat/{dm}/asiakirjat/{dm_up}{year}{n}"
UA = {"User-Agent": USER_AGENT}


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return None, ""


def list_meetings(dm, year, nmax, verbose=True):
    # Key on the unique meeting DATE (robust); the printed meeting number is a
    # best-effort label parsed from the title (a couple can mis-parse — cosmetic).
    meetings = {}                       # "dd.mm.yyyy" -> dict
    misses = 0
    for n in range(1, nmax + 1):
        url = BASE.format(dm=dm, dm_up=dm.upper(), year=year, n=n)
        status, htmlpg = fetch(url)
        time.sleep(0.2)
        if status != 200 or not htmlpg:
            misses += 1
            if misses >= 6 and len(meetings) > 3:    # past the tail -> stop
                break
            continue
        misses = 0
        md = re.search(r'(\d{1,2})\.(\d{1,2})\.' + str(year), htmlpg)
        if not md:
            continue
        date = f"{int(md.group(1)):02d}.{int(md.group(2)):02d}.{year}"
        mt = re.search(rf'Kaupunkiympäristölautakunta\s+(\d+)\s*/\s*{year}', htmlpg)
        num = int(mt.group(1)) if mt else None
        if date not in meetings:
            meetings[date] = dict(meeting=num, year=year, date=date, url=url,
                                  doc_id=f"{dm.upper()}{year}{n}")
            if verbose:
                print(f"  mtg {str(num or '?'):>3}/{year}  {date}  {url}")

    # sort chronologically
    def key(m):
        d, mo, _ = m["date"].split(".")
        return (int(mo), int(d))
    return sorted(meetings.values(), key=key)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dm", default="u540", help="decision-maker id (u540 = Kaupunkiympäristölautakunta)")
    ap.add_argument("--year", type=int, default=2025)
    ap.add_argument("--nmax", type=int, default=45)
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()

    out = args.out or f"{OUT}/meetings_{args.year}.json"
    print(f"listing {args.dm} meetings for {args.year} (probing 1..{args.nmax}) ...")
    meetings = list_meetings(args.dm, args.year, args.nmax)

    import os
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    json.dump(meetings, open(out, "w"), ensure_ascii=False, indent=1)

    # ── sanity check ──────────────────────────────────────────────────────────
    dates = [m["date"] for m in meetings]
    print(f"\nSANITY CHECK")
    print(f"  meetings found : {len(meetings)}")
    print(f"  date span      : {dates[0]} .. {dates[-1]}" if dates else "  no dates")
    print(f"  -> {out}")
    if not meetings:
        sys.exit("NO MEETINGS FOUND — check the dm id / URL scheme")


if __name__ == "__main__":
    main()
