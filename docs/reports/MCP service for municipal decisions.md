# MCP service for municipal decisions

*See also [Questions over decision content](Questions%20over%20decision%20content.md): it
inventories Helsinki's sources beyond this repository, assesses feasibility by question type
and sets out an experiment plan. The summary figures below predate the summary parser fix
of 2 Nov 2026.*

**Recommendation: build it, but as a staged experiment for professional users, and do not launch a public service on today's data.** A read-only MCP server over this repository is technically cheap: a localhost spike on the real data answered tool calls at p50 7.5 ms, and hosting should cost about EUR 0 to 6 a month. The niche also looks open, because no Ahjo or paatokset.hel.fi MCP server was found and the City's own decision API is closed. The hard parts are elsewhere. Only 37 % of located decisions carry a real summary, the `stage` field cannot follow a case to the City Board or Council, and an assistant will restate heuristic fields as fact. The features that would add most value, full decision text above all, are also the ones that bring GDPR duties. Municipal MCP servers exist (OpenCouncil in Greece is the closest), but none publishes usage, so "successful" currently means attention and maintenance rather than proven user value. The ten ordered steps in section 4 test data truth, assistant behaviour and demand before anything goes public, and their first three steps also improve the map if the MCP idea later fails. No lawyer or data protection officer has reviewed any of this, and no Helsinki user has been interviewed.

**How to read the evidence labels.**
- **[Measured]**: re-checked read-only for this report on 2 Nov 2026 against `data/` (datasets generated 1 Nov, Kerro kantasi 20 Oct).
- **[Measured, notes]**: measured by the research notes on the same date and not re-run here, such as live index queries and the localhost spike.
- **[Sourced]**: stated by the linked source. Where the notes saw only a search excerpt, the text says so.
- **[Inference]**: my or the notes' judgement, including all rankings, effort sizes and pass thresholds.
- **[Lawyer/DPO]**: needs a lawyer or data protection officer. Nothing here is legal advice.

## 1. Comparable services exist, but none has proven user value

No MCP server for Ahjo or paatokset.hel.fi turned up in GitHub searches or the official registry, although keyword search cannot prove absence ([Sourced] per the implementations note). Official publishers are rare and national: France, the US and the UK's i.AI, plus an Indian beta known only from a search excerpt. No city government was found publishing its own server. The field is young, and several municipal services date from the past few months.

| Service | Type and operator | Evidence on 2 Nov 2026 | Why it matters here |
|---|---|---|---|
| [data.gouv.fr](https://github.com/datagouv/datagouv-mcp) | National, official, API passthrough | 1,604 stars; [launch traffic overloaded it](https://www.banquedesterritoires.fr/datagouv-facilite-lacces-des-ia-generatives-aux-donnees-publiques) | Strongest case, but a national brand and catalogue, so not a benchmark for one city |
| [onData CKAN](https://github.com/ondata/ckan-mcp-server) | Community, works on any CKAN portal | 3,676 npm downloads a month; reused by [AgID](https://github.com/AgID/ckan-mcp-server) and [listed by Zurich](https://www.stadt-zuerich.ch/de/politik-und-verwaltung/statistik-und-daten/open-government-data/anwendungen/anwendungen-2026/ckan-mcp-server.html) | Best community evidence; reach came from being reusable |
| [OpenCouncil](https://opencouncil.gr/mcp) | Greek non-profit, own corpus | Live, anonymous, 15 tools including `list_nearby_subjects`; [22 contributors](https://github.com/schemalabz/opencouncil); [EUR 100k donation](https://schemalabs.substack.com/p/funds-product-motives?open=false) | **Closest overall match**, with a setup page for non-developers |
| [DIS, Karlsruhe](https://github.com/1612elphi/desinformationssystem) | One person, scraper + LLM enrichment + SQLite FTS5 | Live, 17 tools, 1 star | Closest architecture; official PDF overrides derived values |
| [OpenCityRecord](https://github.com/OpenCityUSA/opencityrecord-mcp) | US commercial beta, 340+ cities and counties | [USD 0 to 499 a month](https://opencityrecord.org/mcp); no user numbers | Never names members of the public or staff |
| [Open Council Network](https://opencouncil.network/api/pricing) | UK commercial, Bearer token | GBP 249 to 549 a month; customers not stated | Shows a price asked, not that anyone pays it |
| [Aura](https://github.com/trotor/aura) | Finnish, Futuai Oy, metadata index | Live, 8 tools, 8 stars | Best Finnish response design: provenance, licence, retrieval time, error hints |
| [Kotihiiri](https://kotihiiri.eu/) | Finnish website, operator unnamed | 55 municipalities, CC BY 4.0, weekly refresh; no MCP or API mentioned | Nearest Finnish neighbour, and it covers Helsinki |

**[Sourced] The honest answer to "successful" is unproven.** No server in the catalogue publishes request counts, retained users or independent answer-quality results. Stars and downloads are weak proxies: [OpenDataMCP](https://github.com/OpenDataMCP/OpenDataMCP) has 156 stars and no push since December 2024. Even data.gouv.fr's coverage reports [slowness on large files and access mainly for advanced users](https://www.banquedesterritoires.fr/datagouv-facilite-lacces-des-ia-generatives-aux-donnees-publiques), and calls the setup hard to audit.

**[Inference] Sustained projects share a pattern.** They have a host institution or paying audience, a hosted zero-install endpoint, a repeat need, and provenance back to the original record. Failures tend to be one-shot wrappers, unmaintained early-hype repositories, or dependents of an unofficial upstream such as [MunicipalMCP](https://github.com/Skatterbrainz/MunicipalMCP). This comes from a small, biased sample and shows correlation only. A single-city Finnish service should expect modest public numbers, roughly the range of Aura or DIS.

**Non-MCP analogues show who pays.** [Hamlet](https://www.niemanlab.org/2026/01/highlighting-the-funniest-moments-this-startup-aims-to-bring-public-meetings-into-the-tiktok-era/) sells mostly to real-estate developers, while its public channel had 164 TikTok followers. [PlanningAlerts](https://www.planningalerts.org.au/) sent 169,230 alert emails in a week yet warns it needs more monthly supporters. [Plural](https://pluralpolicy.com/blog/video-plural-pricing-plans/) charges USD 3,500 and up a year, for state and federal policy teams. No source shows anyone paying specifically for MCP access to municipal decisions.

**The Helsinki gap carries a warning.** [OpenAhjo is archived](https://github.com/City-of-Helsinki/openahjo), and an open-data catalogue note says the API closed with a replacement planned but undated ([seen as a search excerpt](https://www.avoindata.fi/data/en_GB/dataset/4d992f0d-47a5-4645-aaaa-e5f1316bfe40)). The closure date is not settled. The README and the catalogue note point to December 2024, while [a resource note](https://avoindata.fi/data/en/dataset/4d992f0d-47a5-4645-aaaa-e5f1316bfe40/resource/be779e11-d0fe-4345-9263-c92af8214d42) carries a 12/2023 not-in-production marking. The note's 2015 launch date also conflicts with a repository created in 2013. The opening therefore comes with a lesson: official interfaces disappear, and this repository already rests on an undocumented proxy.

## 2. Professional briefing is the best use, and it needs decision text

### Today's data is a good pointer and a poor answer engine

The notes quote different numbers for the same things. These are mostly different denominators, and one is a plain error.

| Figure in the notes | What it counts | Check |
|---|---|---|
| **1,727** records | Located decisions | [Measured] |
| **1,832** | Those plus 105 unlocated decisions | [Measured] |
| **1,912** | Located decisions plus 185 located consultations | [Measured] |
| **2,017** | 1,912 plus the 105 unlocated decisions. It leaves out 19 unlocated consultations; counting them gives 2,036 | [Measured] |
| **1,807** map pins | After deduplication of cases and the Jan–May 2017 overlap. The difference from 1,912 is 105, which only coincidentally equals the unlocated count | [Measured] |
| **42.5 %** no summary | 734 of 1,727 located decisions with an empty field | [Measured] |
| **41 %** no summary | 833 of 2,017 (734 + 77 unlocated + 22 consultations), 41.3 % | [Measured] |
| **37 %** real summary | 636 of 1,727, after also removing 357 boilerplate appeal notices. The notes are compatible, but neither 41 % nor 42.5 % gives the useful number | [Measured] |
| **4,413** / **4,394** zoning plans | WFS today has 4,394 in the main layer plus 37 underground, 4,431 in total. The note's 4,394 is the main layer only. The README's 4,413 is probably an earlier two-layer count, not verified | [Measured], live WFS |
| **185** / **401** hearings | Plan-related filtered subset versus all hearings in the API | [Measured] / [Measured, notes] |
| Lauttasaari **36**, Kruununhaka **7** | Method unstated in the note. I get Lauttasaari 42 (exact word) or 53 (stem) and Kruununhaka 12 or 18. Inflection moves the count, so treat these as indicative | [Measured] |
| 732 / 729 records with attachments | Field present versus non-empty, 4,533 attachments in both cases | [Measured] |
| Trees "14" of 905 | I get 10 to 19 depending on fields and case handling. Order of magnitude holds | [Measured] |

**The number to plan on: 63 % of located decisions (1,091 of 1,727) have no usable decision summary**, split into 734 empty and 357 appeal boilerplate [Measured]. All 357 are `proposal` records from 2017 to 2026, and the notice reads "MUUTOKSENHAKUKIELTO … Kuntalaki 136 §". An assistant may take "no appeal allowed" as the substance of the decision. The cause is probably the parser anchoring on "Päätös" where the page uses "Esitys" [Inference]. From 2018 on, 537 of 874 records (61 %) have a real summary [Measured]. All 624 pre-2017 records have no decision text stored.

**The text exists in the index the scraper already queries.** For the 905 Kaupunkiympäristölautakunta records, `decision_content` and `decision_motion` have medians of 984 and 7,277 characters, about 25 times the 320-character cap [Measured, notes]. The effect on recall is large, as these rough regex matches show.

| Topic in 905 records | Stored fields | Full text [Measured, notes] |
|---|---|---|
| Cycling | 7 | 498 |
| Floor area or residents | 0 | 746 |
| Cost | 0 | 775 |
| Noise | 1 | 242 |

Full-text hits include passing mentions, so this shows what is out of reach, not how many answers are relevant.

**Three structural problems go beyond text.**

Status does not follow a case. Of 298 `hel-` zoning proposal cases from 2017 on, 256 (86 %) also appear in City Board or Council decisions in the index, while the dataset still says `proposal` [Measured, notes]. Outcomes and date order were not parsed. Tabled items are also undercounted: 12 labelled against 31 found in text by rough patterns [Measured, notes].

A pin is not a place. Of 655 zoning records matched by plan number to polygons of plans in force, 81 % of pins fall outside the polygon, 33 % are over 250 m away and 17 % over 500 m [Measured, notes]. Plan-number matching could produce the largest distances wrongly, and the test covers zoning plans in force only. Decisions occupy just 816 distinct coordinates, and 25.4 % sit at district level [Measured].

Accuracy is unknown. All four verdict columns and the notes column in `data/quality_sample.csv` are empty for all 100 rows [Measured]. In addition, 61.1 % of located decisions have at least one of district-level location, stage `other`, no drawing or empty summary, and 569 got their stage from the title alone, including 220 of 715 `approved` [Measured].

### Use cases, ranked

The ranking is [Inference] and a hypothesis, because no Helsinki user research exists. Demand evidence is foreign and indirect. "Now" means what the present dataset can do.

| # | Use case and users | Now | Main missing piece | Best interface |
|---|---|---|---|---|
| 1 | Backgrounder on a place or case: journalists, councillors, assistants | Partial; finds documents, cannot explain why | Decision text, City Board and Council steps | **MCP plausible** |
| 2 | Pipeline monitoring: developers, brokers, suppliers | Poor; floor area in 0 of 905 stored records | Text extraction, status, change feed | Feed or API, MCP as a bonus |
| 3 | Accountability: who voted or dissented | None stored; vote terms in 76 of 905 texts, dissent terms in 4 [Measured, notes] | Text, vote parsing | MCP or website |
| 4 | Precedent search: architects, consultants, lawyers | Almost none | Text, then reports with copyright care | **MCP plausible** |
| 5 | Civic preparation of opinions: associations, NGOs | Partial; only Kerro kantasi deadlines | Display periods, polygons | Website or hosted chat |
| 6 | Longitudinal research | Partial; 2017 source change confounds trends | Bulk text | **Dataset, not MCP** |
| 7 | "What is planned near me?": residents, housing companies | **Misleading** | Polygons, address search | **Website and alerts** |
| 8 | Works coordination: utilities, contractors | Partial; no schedule or extent | Other sources | Unclear |
| 9 | Internal knowledge: city officials | Adds little | Procurement route | Internal tool |

**MCP suits a narrow group today**: people already working in an AI assistant who ask multi-step questions and want citations. A [vendor survey of software firms](https://stacklok.com/resources/state-of-mcp-in-software-2026/) finds developers and data analysts as the primary users, which says nothing about Finnish journalists. How many Helsinki journalists, assistants or planners use MCP-capable clients is **the largest unknown for this choice** (a gap in the notes). Residents are poorly served by MCP: located plan decisions run at 83 to 108 a year citywide since 2018 [Measured], so need is episodic per district, and the City's [Suunnitelmavahti](https://www.hel.fi/fi/uutiset/suunnittelu-ja-kaavoituskatsaus-esittelee-helsingin-ajankohtaiset-suunnitelmat) already alerts on plans going on view. Paid monitoring faces [Hubexo-style](https://www.fonecta.fi/profiili/hubexo-finland/4010557) databases with contacts (directory listing, weak source), which this project should not imitate because of GDPR. Much of the US products' value comes from transcribing video, a barrier Helsinki's text decisions do not have, so US demand evidence transfers only partly [Inference].

### Three possible products, and which one to test

| Option | Content | Effort [Inference] | Verdict |
|---|---|---|---|
| A. Thin pointer | Current JSON behind tools | Days | Useful for testing clients and caveats. Adds little over the map and [paatokset.hel.fi](https://paatokset.hel.fi/fi) search, so **as a demand test it would falsely show no demand** |
| B. Cited decisions | A + fixed summaries, name-stripped decision text, case timeline, plan numbers | About 2 to 3 weeks | **The target**, subject to steps 7 to 9 |
| C. Full corpus | B + PDF and attachment text, comments, votes, alerts, other cities | Months | Not now. Stacks personal-data, copyright, `robots.txt` and quality risks |

**The notes disagree here, and the disagreement is real.** The legal note recommends a first scope of excerpts only. The use-case note warns that launching on excerpts tests the weakest version. These can be reconciled by separating testing from publishing: option A only re-serves what `data/` already publishes and so adds little new legal risk, while option B is evaluated privately and published only after name stripping is measured and reviewed [Inference]. This also implies **full text must not be committed to the public `data/` folder**. Git history would make [erasure](https://gdpr-info.eu/art-17-gdpr/) hard, and the daily job would re-add suppressed items. The engineering note's "image built from `data/`" therefore needs a separate private store for text under option B [Inference].

### How it would work

**The shape is a single stateless Python container with data baked in and five read-only tools, with no authentication** ([Inference] from the engineering note, high confidence in the shape). The current MCP revision, [2026-07-28](https://blog.modelcontextprotocol.io/posts/2026-07-28/), removed sessions and the handshake, so a read-only server now resembles an ordinary JSON-over-POST service. [Older clients cannot fall forward](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning), and it is unconfirmed which era hosted clients speak, so the server should serve both eras on one endpoint, which [the official SDK does](https://py.sdk.modelcontextprotocol.io/run/legacy-clients/).

The stdlib-only rule survives if a new `lautakuntamuistiot/query.py` holds all query logic and only `mcp_server/server.py` imports `mcp`, with its own hash-locked requirements [Inference]. Search is in-memory SQLite FTS5: JSON load 15 ms, index build 15 ms, query about 0.17 ms [Measured, notes]. Finnish needs a place-name gazetteer plus prefix matching plus an instructive hint on empty results. Exact matching found Jätkäsaari in 51 records and "Jätkäsaaressa" in 0, and Snowball missed gradation pairs such as katu/kadun [Measured, notes]. Trigram over-matches badly, with `kaava` hitting 1,075 of 2,017 records. Vector search is not justified yet.

| Tool | Purpose | Design decision |
|---|---|---|
| `search_plans` | Words, place, type, stage, years | Default 10, max 50; attachments excluded |
| `get_plan` | One record in full | Includes drawings, attachments and `appeal: not_provided, see <url>` |
| `find_plans_at_place` | Plans at a **named place only** | Changed from the note's `find_plans_near`, which allows lat/lon and a radius. Those would imply precision that the pin test disproves, and no free-text geocoding is exposed |
| `list_open_consultations` | Hearings still open | Compute from `close_date` at request time. One was open on 2 Nov (Pitäjänmäki, to 31.12.2026) [Measured]; this data is 12 days older than the decision data |
| `summarize_plans` | Counts by year, type, stage | Avoids fetching records for trend questions |

Each response carries a provenance envelope (data version, data date, unofficial status, attribution). Each record carries what varies: `source_url`, `stage` with its basis and "committee stage only" meaning, `location_precision`, `summary_truncated` and `legal_status: unknown`. Field names that carry meaning are more likely to survive restatement than a footer [Inference]; no measurement exists. This merges the legal note's per-record schema with the engineering note's once-per-response envelope, which keeps payloads under client limits. The note's size estimate is about 22,000 characters for 50 records, against a [10,000-token warning in Claude Code](https://code.claude.com/docs/en/mcp).

**Hosting and connection.** Cloud Run in `europe-north1` [should stay within the free grant](https://docs.cloud.google.com/run/pricing) even at a million calls a month [Inference from listed prices], but budgets only alert. With `--max-instances=1`, worst-case abuse is about USD 65 a month plus request fees. [Hetzner in Helsinki](https://www.hetzner.com/cloud/cost-optimized/) at EUR 5.99 excl. VAT gives a hard cap and a European owner, at the cost of patching. Choose it if a city partner asks about sovereignty. Users connect by pasting a URL: [Claude allows one custom connector on the Free plan](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp), and on Team or Enterprise an Owner must add it, a real barrier for staff on managed workspaces. ChatGPT free-plan access is unconfirmed.

### Features, in order

| Priority | Feature | Effort [Inference] | Use cases |
|---|---|---|---|
| Now | Fix parser, recompute stage; plan number as field (derivable for 726 of 775 zoning records [Measured, notes]); ISO dates; stable id from `decision_url` | Up to 2 days | All |
| Now | MCP layer with provenance and refusals | Days | 1–5 |
| Next, if cleared | Name-stripped decision text with cited passages | Up to 2 weeks | 1–5 |
| Next | City Board and Council timeline; keep all decisions per case rather than the "best" one | Up to 2 weeks | 1–3 |
| Then, if demanded | Polygons from the zoning archive; change feed from `update_report`; votes; official-holder decisions (the traffic planning chief alone has 338 "suunnitelm" subjects [Measured, notes]) | Mixed | 2, 3, 5, 7, 8 |
| Check before committing | `kartta.hel.fi/suunnitelmat` for pending plans, documents and schedules; not assessed and could reorder several rows | Half a day | 1, 2, 5, 7 |
| Not now | PDF or report text; comment text; person pages; alerts duplicating Suunnitelmavahti | | |

**The zoning archive deserves a specific decision.** It is not in `data/` (`asemakaava_dataset.json` is absent) [Measured]. It has the cleanest licence ([CC BY 4.0](https://hri.fi/data/api/3/action/package_show?id=helsingin-asemakaavahakemistokartta-asemakaavahakemisto)) and real polygons, and it is the one source where "in force" has an official basis, since the layer lists valid plans. A later tool could say "listed in the City's layer of plans in force as of date X", which the decision dataset can never say [Inference]. It should join by plan number after the decision pipeline is honest, not in v0. Polygons exist only for plans in force, so they cannot fix radius search for pending plans.

## 3. Todos and do-nots follow from one shift: the caveats no longer travel with the data

Today's map is low-risk because it holds short excerpts, links out and shows caveats beside each pin. An LLM-facing service with full text removes all three protections ([Inference], legal note). Refusals built into the tools are stronger than disclaimers.

### Do-nots

| Do not | Why | Basis |
|---|---|---|
| State or compute an appeal deadline | Route, recipient and service date all vary, the data has no publication date, and 47.9 % of records are proposals that may not be appealable at all | [Sourced] [Kuntalaki 134–140 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@), [Kuntaliitto](https://www.kuntaliitto.fi/laki/muutoksenhaku/kuntalain-oikaisuvaatimus); [Measured] share |
| Describe a decision-dataset plan as "valid" or "in force", or use `approved` without "by the committee" | No such field exists | [Measured] |
| Answer "nothing is planned here" | Keyword filter, 105 unlocated, 2013 floor, no official-holder decisions | [Measured] and [Inference] |
| Return radius answers from pins, or spread pin positions | Pin test above; 48.1 % of per-type GeoJSON pins are offset [Measured, notes]. Serve true points with precision | [Measured, notes] |
| Offer search by person name | Creates a profile the City's site does not; closest to mass dissemination | [Inference] from [*Satakunnan Markkinapörssi* commentary](https://inforrm.org/2017/07/06/case-law-strasbourg-satakunnan-markkinaporssi-oy-and-satamedia-oy-v-finland-no-journalism-exception-for-massive-exposure-of-personal-taxation-data-dirk-voorhoof/), [*Google Spain*](https://huntonak.com/privacy-and-information-security-law/eu-court-justice-upholds-right-erasure-google-search-case); **[Lawyer/DPO]** |
| Bulk-crawl `ahjojulkaisu.hel.fi` for text | [`Disallow: /`](https://ahjojulkaisu.hel.fi/robots.txt), and it hosts 857 of the 1,581 drawing links [Measured]. A sampled PDF sent `x-robots-tag: noindex` | [Sourced] |
| Return substantial text from consultants' reports, photos or letters | [Section 9(2) carve-out](https://www.edilex.fi/tekijanoikeusneuvosto/fi/20200004.pdf). The [YM 22/2018 report](https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/161120/YMra_22_18_Rakennettua_ymparistoa_koskevan_tiedon_tekijanoikeus.pdf?sequence=1&isAllowed=y) is the nearest source, with thesis-level weight. [13 b §](https://finlex.fi/api/media/statute/9863/mainPdf/main.pdf) covers mining copies, not republication | [Sourced] and [Inference] |
| Ingest Kerro kantasi comments | [CC BY-NC-SA, and identified users' data is not disclosed](https://github.com/City-of-Helsinki/kerrokantasi-ui/blob/main/cities/helsinki/i18n/service-info/content.en.md) | [Sourced] |
| Expose a geocoding tool or call public Nominatim per query | [Usage policy has an explicit LLM clause](https://operations.osmfoundation.org/policies/nominatim/). A general tool also undercuts the [geocoding guideline's](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Geocoding_-_Guideline) non-substantial position | [Sourced] and [Inference] |
| Pass LLM queries through to the Elasticsearch proxy, or expose a fetch-any-URL tool | Unbounded agent loops on an undocumented backend; [SSRF](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html) | [Sourced] and [Inference] |
| Rate-limit tightly by IP | [Claude's traffic comes from one range](https://claude.com/docs/connectors/building/authentication), and [WAF 429s break connectors](https://claude.com/docs/connectors/building/troubleshooting.md) | [Sourced] |
| Log query text, place names or full IPs | People may search their home street. A documented deviation from [OWASP's "log full parameters"](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html) | [Inference] |
| Rely on the journalism or research exemptions | [27 § and 31 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2018/1050/fin@) fit an automated public service poorly | [Inference]; **[Lawyer/DPO]** |
| Call it official or imply City endorsement | Project states independence; [data.gouv warns of impostors](https://www.data.gouv.fr/posts/experimentation-autour-dun-serveur-mcp-pour-datagouv) | [Sourced] |
| Publish auto-generated summaries without labelling or review | [AI Act Art. 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50) may become live | [Inference]; **[Lawyer/DPO]** |

### Todos

| Todo | Detail | Basis |
|---|---|---|
| Complete the 100-record review | Accuracy currently cannot be stated | [Measured] |
| Link every claim to its original | `source_url` in every result, plus attribution for City data, Kerro kantasi (ODbL) and OpenStreetMap coordinates, per [ODbL 4.3](https://opendatacommons.org/licenses/odbl/1-0/) | [Sourced] |
| Keep Kerro kantasi data as a separate downloadable ODbL dataset | 185 of 401 hearings is likely Substantial; keeping it separate protects the decisions dataset from share-alike | [Inference]; **[Lawyer/DPO]** |
| Strip names, phones and emails from any text served | Decision pages name officials with contact details: a sample of four 2017–2024 pages each had 3–6 @hel.fi emails [Measured, notes]. Prevalence of private persons' names is **unmeasured** | [Sourced] [140 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@) and [Inference] |
| Detect later source changes | `seen_decisions` means nothing notices a later City redaction | [Sourced] README; [Inference] on the effect |
| Before public launch: name an operator, publish a privacy notice and an erasure route | Suppression must survive re-scrapes and cover git history. Legitimate-interest assessment per [EDPB 28/2024](https://www.edpb.europa.eu/system/files/documents/2025-05/edpb_opinion_202428_ai-models_fi.pdf) | **[Lawyer/DPO]** |
| Ask the City in writing | Proxy use, replacement API, attachment licence, retention | See step 1 |
| Add a source-adapter layer and a go-live gate | Refuse deployment if record count falls sharply or schema changes | [Inference] |
| Deploy from a separate workflow | [`GITHUB_TOKEN` commits do not fire push workflows](https://docs.github.com/en/actions/concepts/security/github_token), so use `workflow_run`. The scraping job should hold no deploy credentials | [Sourced] and [Inference] |
| Harden the SDK defaults | [`FastMCP` is now `MCPServer`](https://py.sdk.modelcontextprotocol.io/migration/). The spike found GET `/mcp` holding connections open, `ttlMs: 0`, and `listChanged`/`subscribe` advertised. Set `allowed_hosts`, 405 on GET, body and query caps, FTS5 quoting, instance cap | [Sourced] and [Measured, notes] |
| Treat scraped text as hostile | Strip control characters and HTML, cap field lengths, allowlist output URLs. [Pattern checks cannot establish safety](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html), and the risk grows with full text | [Sourced] and [Inference] |
| Check directory rules before submitting | [Anthropic](https://claude.com/docs/connectors/building/review-criteria) needs `readOnlyHint`, documentation, privacy policy and support contact. [OpenAI](https://developers.openai.com/apps-sdk/app-submission-guidelines) forbids presenting an app as a trial or demo, which conflicts with "experimental" wording | [Sourced] |
| Count aggregates only | Tool, status, duration bucket, zero-result boolean. Unique users are not measurable without identifying people | [Inference] |

### Items that stay with a lawyer or DPO

These are unresolved. The notes found **no current Ombudsman decision on third-party re-publication or LLM indexing of municipal decisions**.

| Question | Why it matters |
|---|---|
| Is Art. 6(1)(f) a sound basis, and is a DPIA needed? | The working assumption; a DPIA was not established as mandatory |
| What does [140 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@) mean for a re-publisher? | It binds the City to remove personal data after the appeal period. No provision read addresses mirrors. One closely inspected 2021 page still carried a contact block about five years on |
| How should the GDPR Art. 14 notice work for people named in source text? | The disproportionate-effort exception was not verified in the notes |
| Are officials' names in role lower risk ([4 § 1 kohta](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2018/1050/fin@))? | Decides whether any names can stay |
| Does `robots.txt` count as a text-and-data-mining reservation? | Unsettled; no Finnish authority found. The City may not be the rightholder for consultant material |
| Does the OSM geocoding safe harbour hold, including for commercial use and if coordinates are partly migrated to City data? | The geocoding and collective-database guidelines are not fully aligned |
| Would a paid service change exposure under [25 d §](https://www.edilex.fi/tekijanoikeusneuvosto/fi/20200004.pdf) and the [new product liability directive](https://cms.law/en/int/publication/the-new-eu-product-liability-directive-eu-2024-2853)? | Purpose wording fits civic scrutiny better than commerce, and free open-source and pure information have exclusions. The status of the Finnish bill is unknown |
| Is semantic search with embeddings an "AI system"? | [Definition](https://artificialintelligenceact.eu/article/3/) grey area; deterministic retrieval is probably outside |
| What liability follows wrong property or appeal information? | Tort Liability Act and the land-use act's appeal provisions were not reviewed |

Two corrections from the legal note prevent mis-citation [Sourced]. The removal rule for minutes is Kuntalaki **140 §**, while 108 § covers notices. A Copyright Act **13 c § could not be confirmed**, so only 13 b § should be cited.

The City's DPO can explain the City's retention practice, but cannot clear this project's own controller duties [Inference]. Both a City contact and independent advice are therefore needed.

## 4. Ten ordered experiments decide whether this deserves to go public

**All thresholds are my proposals, not benchmarks.** The notes found no published targets for tool selection or civic MCP adoption. Effort is estimated with no team plan behind it, and the whole sequence looks like about 8 to 10 part-time weeks. Steps 1 to 3 are worth doing even if the MCP idea dies. Steps 7 to 10 use data beyond what `data/` publishes today and stay private.

### Step 1: Ask the City, and engage legal review (start in week 1, replies arrive later)
Send written questions via [HRI](https://hri.fi/fi/yhteystiedot/) and a [helsinki-paatokset](https://github.com/City-of-Helsinki/helsinki-paatokset) issue, and to the City's DPO (tietosuoja(a)hel.fi, an address seen via search summary only). Ask: may third parties use the Elasticsearch proxy, and at what rate? Is there a timeline for the replacement API? Is authenticated Ahjo access possible? What is the attachments' licence, what retention rule applies, and how many Suunnitelmavahti subscribers exist? That last figure would be the best local demand signal. Separately, brief a lawyer on the table in section 3.
**Pass:** a written answer that does not prohibit the use, and a lawyer or DPO view on the legal basis, both within 6 weeks. **Fail:** a refusal means no proxy-based public service. Silence means stay private and file a [Julkisuuslaki 16 § 2 mom.](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/1999/621/fin@) bulk request through Kirjaamo (original 1999 text read; later amendments unchecked).

### Step 2: Complete the quality review (about 1 day)
Fill in `data/quality_sample.csv`, and add 30 extra title-only `approved` records from 2013 to 2017, which the random sample underweights. Publish the results.
**Pass:** at most 10 wrong of 100 in each of type, stage and drawing, and location correct at its tagged precision in at least 85 of 100. Zero errors would bound the rate at about 3 %, and 10 errors implies about 5 to 17 % (legal note's estimate). **Fail:** that field is exposed only as `unverified`, never as a filter, and the failing heuristic is fixed before step 5.

### Step 3: Fix the parser and add honest fields (up to 2 days)
Replace the boilerplate summaries, then add `stage_basis`, `summary_truncated`, plan number, ISO date and an id derived from `decision_url`. The README's upsert key collides on 2 records (U540 `hel-2018-009468` and `hel-2013-005863`, both `liikenne`) [Measured], which should be checked as a possible data bug.
**Pass:** 0 of the 357 notices remain, every stage change appears in a logged diff, plan number covers at least 726 of 775 zoning records, and a hand check of the 19 suspected tabled decisions finds them relabelled or flagged. **Fail:** any unexplained record loss or stage change blocks merging.

### Step 4: Deploy a thin server and connect real clients (2 to 4 days)
Build `query.py`, the five tools and hardening on Cloud Run under an unlisted HTTPS URL, because hosted clients connect from vendor clouds and cannot reach localhost. Serve only what `data/` already publishes. The spike tested only `curl` on localhost, so client behaviour is the first real unknown.
**Pass:** Claude custom connector, VS Code and, if plan access allows, ChatGPT developer mode each complete all five tools from a cold start; [Inspector](https://modelcontextprotocol.io/docs/tools/inspector) and the [conformance suite](https://github.com/modelcontextprotocol/conformance) pass; 405 on GET breaks no legacy client; hosted p95 is under 1 s. Record the protocol era each client uses. **Fail:** a cold-start failure means a warm instance (about USD 9.70 a month) or Hetzner. An era failure is fixed in configuration before step 5.

### Step 5: Run the baseline agent eval on excerpts (2 to 3 days)
Write 40 to 60 tasks, half Finnish and 25 % held out, on [Anthropic's method](https://www.anthropic.com/engineering/writing-tools-for-agents), including the misleading questions: "has this plan been approved?", "can I still appeal?", "is nothing planned on my street?", "summarise this decision". Run on Claude and one GPT model.
**Pass:** zero stated appeal deadlines and zero "valid" or "in force" claims across all runs (hard gate); at least 90 % of stage answers keep the committee-only meaning; at least 95 % of factual claims cite a `source_url` that exists in the data; at least 80 % task success on answerable tasks; Finnish within 10 points of English. **Fail:** redesign fields and refusals and rerun once. If the hard gate still fails, field-level caveats do not survive in practice, and public MCP stops here in favour of a website or feed where the service controls the wording. These results measure the server, not the truth of the data, which is why step 2 comes first.

### Step 6: Interview professionals with the demo (2 weeks elapsed)
Interview at least 8 people across local journalists, councillors' assistants, planning consultants and a developer or broker. Nobody in these groups has been consulted yet. Ask what they do now, how often and at what cost, since **no sourced figure for any Finnish group exists**, and which clients their workplace permits.
**Pass:** at least 3 name a task recurring at least monthly that the demo would serve once it has text, and at least 3 already use or may use an MCP-capable client. **Fail:** MCP is the wrong interface. Publish the fixed dataset and a feed, and keep the map. If location questions dominate, spend half a day assessing `kartta.hel.fi/suunnitelmat` before anything else.

### Step 7: Test name stripping on real decision text (3 to 5 days)
Fetch `decision_content` and `decision_motion` for a stratified sample of 100 decisions at low rate, stored locally, outside git, and deleted afterwards. Tell the legal reviewer this is happening. Hand-tag names and contacts, build rules on 50, and test on the other 50.
**Pass:** on the hold-out, zero private persons' names and zero phone numbers or emails, plus a measured prevalence figure for the reviewer. **Fail:** public text stays at excerpts, or only the decision clause without reasoning. Name stripping in Finnish text may not reach zero by rules, so this is a real test and not a formality.

### Step 8: Compare stripped text against excerpts (1 week)
Extend the private store to the 905 records, and add passage search with cited snippets. Rerun step 5's task set plus precedent and backgrounder tasks with a hand-checked answer key.
**Pass:** at least 20 points better task success on use cases 1 and 4 than excerpts, hard gate still clean, payloads within limits. **Fail:** text does not earn its legal cost, so stay with option A and reconsider the whole service. The largest gain expected is on topic questions, but passing mentions could inflate recall without improving answers, which is exactly what this measures.

### Step 9: Build and hand-check the case timeline (up to 2 weeks)
Link each case to City Board and Council decisions by case id, and keep all decisions per case rather than the "best" one. Hand-check 30 random linked cases.
**Pass:** at least 27 of 30 have correct links and date order, the tools show "last known step, as of date", and the eval's status questions improve. **Fail:** status stays explicitly committee-only with a link to the case page, and use case 2 is dropped.

### Step 10: Run a closed pilot (4 weeks)
Invite 5 to 10 interviewees, with their consent, using minimal aggregate metrics plus a one-question weekly check-in, since logs cannot count people.
**Pass:** at least 3 report real work use in at least 3 of 4 weeks, at least one names a task shortened or replaced, and no reported legal-status error remains unresolved after 2 working days. **Fail:** end the endpoint and publish dataset and feed only.

**Public beta is a decision, not an experiment.** It requires passes at steps 1, 2, 5 and 10, and at steps 7 and 8 if any decision text is served, plus a named operator, privacy notice, erasure route, Finnish setup page and registry listing. A paid tier should not be considered until the legal questions above are answered, and [Plural-level pricing](https://pluralpolicy.com/blog/video-plural-pricing-plans/) looks a stretch for one city. Grants, a consultancy-led offer or other Finnish cities are the credible routes, and all are untested [Inference].

## Conclusion

The research changes what the project is. The MCP server is the smallest and least risky component, a few days' work on a stateless protocol. The real product is a name-stripped, citable record of what happened in each case, with status that follows it through the City Board and Council. That record would improve the map, a feed and a dataset whatever happens to MCP, so the interface decision can wait for evidence while the data work cannot. The review of 100 records is the cheapest high-value act available: until it is done, nobody can state how accurate any of this is.

The most useful outcome may also be a modest one. If step 5 shows that assistants drop caveats whatever the field design, or step 6 shows that local professionals do not work in MCP clients, the right response is a better open dataset that others can build on. Kotihiiri, Aura or a City replacement API could carry it, though no contact has been made and any such federation is only a hypothesis. The City's planned API could also remove the proxy risk, or the niche, on a date nobody can currently name, which is a further reason to keep the investment small until the pilot reports.
