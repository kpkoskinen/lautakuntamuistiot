#!/usr/bin/env python3
"""
What did an update change on the map? Compares the layers in data/umap/ with the
last commit and lists, per layer, the pins added, changed and removed
(pins only nudged aside to make room for a new neighbour are just counted).

    python3 -m lautakuntamuistiot.update_report                       # print it
    python3 -m lautakuntamuistiot.update_report --log data/update_log.md

The daily job runs it before committing: the text goes to the run's summary page, and
--log adds it to the top of the update log in the repository, so every update that
changed something is recorded with what it added. The first line of the output is a
one-line summary, used as the commit message.
"""
import argparse, json, os, subprocess, time

from .build_kml import ORDER

LAYERS = "data/umap"


def features(path, rev=None):
    """{asia_id: feature} of a layer file, from the working tree or a git revision."""
    try:
        if rev:
            r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
            if r.returncode:
                return {}
            data = json.loads(r.stdout)
        else:
            data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {f["properties"]["asia_id"]: f for f in data["features"]}


def _content(f):
    """A feature's properties without the pin-offset note, to tell a real change from a
    pin only nudged aside to make room for a new neighbour."""
    p = dict(f["properties"])
    p["description"] = "\n".join(l for l in p.get("description", "").split("\n")
                                 if not l.startswith("Location:"))
    return p, f["properties"]["description"].rsplit("Location:", 1)[-1].split(";")[0]


def report(layers=LAYERS, rev="HEAD"):
    lines, tot = [], {"added": 0, "changed": 0, "removed": 0, "nudged": 0}
    for k in ORDER:
        path = f"{layers}/{k}.geojson"
        old, new = features(path, rev), features(path)
        added = [new[a] for a in new if a not in old]
        removed = [old[a] for a in old if a not in new]
        diff = [a for a in new if a in old and new[a] != old[a]]
        changed = [new[a] for a in diff if _content(new[a]) != _content(old[a])]
        nudged = len(diff) - len(changed)
        tot["nudged"] += nudged
        if not (added or removed or changed):
            continue
        tot["added"] += len(added); tot["changed"] += len(changed); tot["removed"] += len(removed)
        lines.append(f"- **{k}**: +{len(added)} added, {len(changed)} changed, "
                     f"{len(removed)} removed")
        for tag, fs in (("+", added), ("~", changed), ("−", removed)):
            for f in fs:
                p = f["properties"]
                lines.append(f"  - {tag} [{p['name']}]({p['decision_url']})")
    head = (f"Data update {time.strftime('%Y-%m-%d')}: {tot['added']} pins added, "
            f"{tot['changed']} changed, {tot['removed']} removed")
    if tot["nudged"]:
        lines.append(f"- {tot['nudged']} other pins moved a few metres to make room")
    if not (tot["added"] or tot["changed"] or tot["removed"]):
        head = f"Data update {time.strftime('%Y-%m-%d')}: datasets updated, map unchanged"
    return head, lines


def main():
    ap = argparse.ArgumentParser(prog="python3 -m lautakuntamuistiot.update_report")
    ap.add_argument("--layers", default=LAYERS)
    ap.add_argument("--rev", default="HEAD", help="git revision to compare with")
    ap.add_argument("--log", default=None, help="add the report to the top of this markdown file")
    args = ap.parse_args()
    head, lines = report(args.layers, args.rev)
    text = "\n".join([head, ""] + lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("## 3. Changes\n\n" + text + "\n\n")
    if args.log:
        title = "# Update log\n\nWhat each automatic update changed on the map, newest first.\n\n"
        try:
            body = open(args.log, encoding="utf-8").read()
            body = body[len(title):] if body.startswith(title) else body
        except OSError:
            body = ""
        entry = f"## {head}\n\n" + ("\n".join(lines) + "\n\n" if lines else "")
        with open(args.log, "w", encoding="utf-8") as f:
            f.write(title + entry + body)


if __name__ == "__main__":
    main()
