# Project lifecycle and meeting data

**Summary.** The most useful thing this repository could offer, through MCP or anything else, is the **path of a project**: from first plans through Kerro kantasi, revised plans and the project decision to the approval of detailed plans, with every document and meeting linked along the way. People will ask "what is on the next meeting?", "what plans are active in this area?", "has this been decided already?" and "show me all plans and meetings about Kruunusillat". The earlier report, [MCP service for municipal decisions](MCP%20service%20for%20municipal%20decisions.md), treated single decision records as the unit and saw a case timeline only as a fix for the `stage` field, so it did not look at this. The current data already holds much of the raw material: case ids in 2017 → records, zoning plan numbers that bridge the 2017 source change, and consultations with dates and places. But it throws the path away by keeping one "best" record per case. It also cannot see projects above the case level, decisions taken by the City Board and Council, or upcoming agendas. The next step is a hands-on trace of four projects through the City's own sites. That trace is **blocked** in the cloud session that wrote this, because its network policy denies the City's hosts (see section 6).

Written on 2 Nov 2026 from a discussion with the repository owner and read-only checks of `data/` (decision data generated 1 Nov, Kerro kantasi 20 Oct). Nothing here has been checked against live City pages yet.

**Evidence labels**, as in the earlier report:
- **[Measured]**: computed from `data/` for this report.
- **[From code]**: read from this repository's source.
- **[Background]**: general knowledge of Finnish planning practice, not checked for Helsinki's current practice. Verify before relying on it.
- **[Inference]**: judgement.
- **[Decided]**: agreed in the 2 Nov discussion.

## 1. Decisions so far

| Topic | Decision | |
|---|---|---|
| MCP prototype | A quick server over `data/` was built before the earlier report had been read, then scrapped. It broke several of that report's do-nots, among them radius search from spread pins and `approved` without "by the committee" | [Decided] |
| Option A (thin MCP pointer) | Not a product or a demand test. Possibly worth doing later as a learning exercise, because we have no experience of running such a service | [Decided] |
| Quality review, contacting the City | Not now. No value proposition or product is being defined yet. The earlier report's route of asking the City and a lawyer first is not being taken | [Decided] |
| Votes | Count only **party-level sums**. Never build a registry of people. The minutes are public documents, and what we avoid is a person-level index | [Decided] |
| Priority | The project lifecycle matters more than individual votes | [Decided] |

On party-level votes, two cautions remain [Inference]:
- **Attribution must be right.** "Party X voted against" is a public claim about a party. Each vote needs the meaning of each option (the proposal, or whose counter-proposal), a link to the minutes, and a hand check while the numbers are small.
- **Small groups are not anonymous.** In a committee of about 13, one party's sum can be one person. That is acceptable because the minutes are public, but the data should not be described as anonymous.

## 2. What the current data already shows

### Three examples

**Kruunusillat** (tram line and bridges from Laajasalo to the centre) [Measured]. A search for "kruunusil" finds only 5 records:
- 04.11.2014 and 11.11.2014: preliminary traffic plan, planning committee
- 12.05.2015: traffic plan, planning committee
- 10.10.2016: Kerro kantasi, Hakaniemenranta and Sörnäistenranta plans
- 16.05.2017: street plans at Kruunuvuorenranta, works committee

After 2017 the name disappears, although the project went on through zoning, a City Council project decision and construction. Later documents use part names ("raitiotie", "Kruunuvuorensilta", Hakaniemi, Merihaka), or were decided by bodies the scrapers do not collect: the City Board, the Council and officeholders. **A project groups many cases under names that change**, and nothing in the data links them.

**Kruunuvuorenranta** (district) [Measured]. "kruunuvuor" finds 39 records from 2014 to 2026: zoning drafts and proposals, street, park and traffic plans, consultations, and a zoning change returned for further preparation in June 2026. They cover 18 distinct `hel-` case ids. That is a good flat list for "what has happened in this area", but nothing says which items are still open.

**Hakaniemenranta** [Measured]. A 2016 consultation ("Hakaniemenrannan ja Sörnäistenrannan suunnitelmat"), the February 2017 zoning draft and the 2018 idea competition consultation are clearly one project. They link only by name and time.

### Linking material in the data

| Link | Finding | |
|---|---|---|
| Case id (`hel-YYYY-NNNNNN`) | Present on 995 records from 2017 on. Case years go back to 2011, so cases started before 2017 still carry them | [Measured] |
| One record per case | 1,649 distinct ids for 1,727 located decisions. Only **70 cases have more than one record**, because `better_decision` keeps one "best" record per case. The path is discarded by design | [Measured], [From code] |
| Cases seen in more than one committee | 20, typically the 2017 handover from the planning committee to Kaupunkiympäristölautakunta. Example: Stansvikinkallio `hel-2015-004954` on 24.01.2017, then 14.11 and 21.11.2017 | [Measured] |
| Stages within multi-record cases | 60 are proposal only, 6 approved plus proposal, 3 proposal plus returned. The final City Board or Council step is never there | [Measured] |
| Pre-2017 records | 732 records from the decision bulletins (*Päätöstiedote*) have `hela-<guid>` ids, **no case id** | [Measured] |
| 2017 overlap duplicates | 85 `hela-` records have a `hel-` twin with the same date and title | [Measured] |
| Zoning plan number (`nro 1xxxx`) | In the text of 726 of 775 zoning records. 651 distinct numbers. **118 numbers appear under more than one record id, and 44 of them join a `hela-` record to a `hel-` record**, so plan numbers bridge the 2017 source change | [Measured] |
| Street and park drawing numbers (`nro 3xxxx/n`) | In 306 of 895 street, park and traffic records. They identify a drawing, not a project | [Measured] |
| Kerro kantasi | 185 records, **no case id and no plan number** in the stored fields. 22 carry a plan-type subtype. Labels name places and themes (Puistot 27, kaavoitus 27, liikenne 26, raitioliikenne 10). Linking to decisions has to use place, name and time | [Measured] |

## 3. A model: project, case, step

| Level | Example | Holds | Likely source |
|---|---|---|---|
| **Project** | Kruunusillat, Hakaniemenranta | many cases and consultations, name aliases, area | Partly curated by hand for large projects. Candidates: the annual *Kaavoituskatsaus*, `kartta.hel.fi/suunnitelmat` (described as holding project documents, schedules and contacts), project sites such as kruunusillat.fi |
| **Case** | `hel-2015-004954` | every decision on it, by every body | The case page and its *Päätöshistoria* (decision history) section on paatokset.hel.fi |
| **Step** | consultation, draft, proposal, approval, appeal, legal force | date, body, meeting, document, outcome | Decisions, agendas, minutes, Kerro kantasi, the zoning WFS for plans in force |

**Typical paths** [Background, verify for Helsinki]:
- **Zoning plan:** start and participation plan (OAS) → draft, often with a consultation → proposal put on public view → committee proposal to the City Board → City Board → City Council (some smaller changes are decided lower down) → appeals → legal force. Finland's land-use act was reformed around 2025, so the names of the steps and the deciding bodies should be checked against current law.
- **Street and park plans:** draft → resident event or consultation → plan on public view → committee approval.
- **Large projects** such as Kruunusillat add a project decision by the Council and an implementation phase, with many street plans and permits.

**Bodies** whose documents a path crosses [Inference]:
- the committee (lautakunta), and possibly its sub-committees (jaostot)
- the City Board and the City Council
- officeholders, who decide without a meeting, so there are no votes. The earlier notes found 338 "suunnitelm" subjects for the traffic planning chief alone

## 4. The questions, and what each needs

| Question | Needs | Today |
|---|---|---|
| "What is on the next meeting?" | Agendas (*esityslistat*) published before the meeting, per body | Not collected. Unknown whether the Elasticsearch index holds agendas or meetings |
| "What plans are active in this area?" | A definition of "open": a case or project with no final step yet, or the City's project map. Area by place name or polygon | Flat list by name only. Nothing is marked open |
| "Has this been decided already?" | The final body's decision for that plan type, and ideally legal force (the zoning WFS lists plans in force) | Stops at the committee. 86 % of zoning proposals from 2017 on also appear in City Board or Council decisions (earlier report) |
| "Everything about Kruunusillat" | The project level, with aliases and case lists | Not possible. The name covers 5 records |

Answer design follows the earlier report's rules [Inference]:
- Say "last known step, as of date" rather than "approved" or "in force".
- Never answer "nothing is planned here".
- Link every step to its source.

## 5. Document types to examine

| Type | Where | In `data/` today | Interest for the lifecycle |
|---|---|---|---|
| Decision page | paatokset.hel.fi, 2017 → | Yes, 995 records, as one heading, a 320-character summary and a drawing link | Its sections include *Päätösehdotus*, *Käsittely*, *Päätöshistoria*, *Esittelijä*, *Muutoksenhaku*, *Lisätiedot*, all cut off by the parser [From code: `common._STOP`]. *Päätöshistoria* is the case path |
| Decision bulletin (*Päätöstiedote*) | www.hel.fi/static/public/hela, 2013–2017 | Yes, 732 records | Short. Probably no history or votes, unverified |
| Full minutes (*pöytäkirja*) | hela archive (other folders?), PDF minutes archive 2011–2023 | No | Attendance, votes, counter-proposals, tabling |
| Agenda (*esityslista*) | paatokset.hel.fi | No | "Next meeting", and the proposal before the outcome |
| City Board and Council decisions | paatokset.hel.fi and the index | No | The final step for zoning and project decisions. The Council's 85 members make party sums meaningful |
| Officeholder decisions | paatokset.hel.fi and the index | No | Many traffic plans. No meeting |
| Kerro kantasi hearing | kerrokantasi.api.hel.fi | Yes, 185 plan-related of about 401 | Early steps. Comments are not to be ingested (CC BY-NC-SA, earlier report) |
| Project map | kartta.hel.fi/suunnitelmat | No | Pending projects with schedules. Not assessed |
| Zoning plans in force (WFS) | kartta.hel.fi | Separate zoning-archive product, not in `data/` | Legal force, polygons, joined by plan number |

The Elasticsearch index that `scrape_decisions.py` queries also holds `decision_content` and `decision_motion`, which the scraper does not request (earlier report). Its full field list, and whether other indices exist (meetings, agendas, cases), is unknown: the mapping request was blocked from this session.

## 6. Next step: trace four projects end to end

Instead of a random sample, follow real projects and record every document and how it links to the next one.

1. **Kruunusillat**: traffic plan, zoning, Council project decision, street plans, the bridges.
2. **A Kruunuvuorenranta zoning case**, for example Stansvikinkallio (`hel-2015-004954`, plan 12410), from draft to Council and legal force.
3. **A street plan** from draft to committee approval, ideally one with a consultation.
4. **Hakaniemenranta**: consultations 2016 and 2018, then zoning.

For each document, record:
- type, body, meeting date, publication date
- which ids it carries: case id, plan number, drawing number, hearing id
- which other documents it links to, and whether the link is explicit (case id, history list) or only by name
- the sections present: *Käsittely* and *Päätöshistoria*, attendance with or without party groups, votes and options
- whether older documents still carry names (Kuntalaki 140 §: the City should remove personal data from the web after the appeal period, so vote lists may vanish from older minutes)

Also check:
- whether upcoming agendas can be read, and how far ahead
- the index fields and any other indices
- what `kartta.hel.fi/suunnitelmat` offers, and in what format
- whether Kotihiiri (55 municipalities, CC BY 4.0, covers Helsinki) already links cases or meetings

Keep the load low, like the daily job, and store nothing beyond notes. **Output:** an addendum to this report with real excerpts and a verdict per link: automatic, matchable, or hand-curated.

**Blocked.** The session's network policy denies these hosts:
- `paatokset.hel.fi`
- `paatokset-elastic-proxy.api.hel.ninja`
- `www.hel.fi`
- `ahjojulkaisu.hel.fi`
- `kartta.hel.fi`
- `kerrokantasi.api.hel.fi`

They must be added under the cloud environment's **Allowed domains** ([steps](https://code.claude.com/docs/en/cloud-environments#network-access)), or the trace must run on a local machine.

## 7. Open questions

- Is the project level curated by hand for large projects only, or derived? How many projects would need curation?
- What counts as "active": a case with no final step, a project on the City's map, or both?
- Should the dataset keep **all** decisions per case, instead of the best one per case, for the map too? That changes `better_decision` and the map's deduplication.
- Which source is authoritative when they disagree: decision history, project map, or WFS?
- Is "next meeting" in scope, given that agendas change and items get tabled?
