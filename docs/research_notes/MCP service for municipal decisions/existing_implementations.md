# Existing MCP servers and civic-tech analogues for municipal, legislative and government data

**Observation date for all metrics: 2026-11-02**, unless a row says otherwise.

How the numbers were collected:

- GitHub figures come from the GitHub API. "Commits" means default-branch commits since 2026-08-01. The query was capped at 100, so "100+" means at least 100.
- npm figures cover 2026-09-30 to 2026-10-29 (api.npmjs.org). PyPI figures are "last month" (pypistats.org).
- "Live" means this research sent an anonymous MCP `initialize` and `tools/list` to the endpoint on 2026-11-02 and got a real response. HTTP 401 means the endpoint exists but needs credentials.

How to read the signals:

- No server in this catalogue publishes request counts or active users. Stars, forks and downloads are weak proxies, and downloads include CI and bots.
- GitHub's `pushed_at` date is misleading. `i-dot-ai/lex` shows a push on 2026-11-02 and `i-dot-ai/parliament-mcp` on 2026-10-30, yet both have 0 default-branch commits since 1 August. The pushes are probably to non-default branches, though that was not checked.

## Which MCP servers exist for municipal, legislative, court, procurement and open-data sources, and which are official?

### Takeaway
Governments have published a small number of MCP servers, all national: France, the US (GovInfo, Census), the UK's i.AI, and India by press report. Almost all are labelled experimental or preview. No municipal government was found publishing its own server. No official or community MCP server for Ahjo or paatokset.hel.fi was found, so this project's niche appears unoccupied in MCP. Greece's OpenCouncil, OpenCityRecord (US), Open Council Network (UK) and a one-person Karlsruhe project are the nearest municipal comparables.

### Cited Findings

**Official or government-linked servers**

| Server | Publisher and status | GitHub metrics | Tools and hosting | Auth and backend | Adoption evidence |
|---|---|---|---|---|---|
| [datagouv/datagouv-mcp](https://github.com/datagouv/datagouv-mcp) | French national portal; [announced as experimental on 25 Feb 2026](https://www.data.gouv.fr/posts/experimentation-autour-dun-serveur-mcp-pour-datagouv) | 1,604 stars, 141 forks, 15 contributors, 9 commits | Live at `mcp.data.gouv.fr/mcp` with 10 tools (7 at launch): dataset, dataservice and organisation search, `query_resource_data`, `get_metrics`. Remote HTTP | No auth; read-only; passthrough to platform APIs | Strongest in this class. [Launch traffic caused repeated redirects to a maintenance page](https://www.banquedesterritoires.fr/datagouv-facilite-lacces-des-ia-generatives-aux-donnees-publiques). No usage figures published |
| [GovInfo MCP](https://github.com/usgpo/api/blob/main/docs/mcp.md) | US Government Publishing Office; [public preview since 22 Jan 2026](https://www.govinfo.gov/features/mcp-public-preview) | [usgpo/api](https://github.com/usgpo/api): 287 stars, 95 forks (the whole API repo, not MCP only) | 2 tools: `searchGovInfo`, `describePackageOrGranule`. Remote at `api.govinfo.gov/mcp` | `x-api-key`; API passthrough (endpoint returned 401 unauthenticated) | No usage figures |
| [uscensusbureau/us-census-bureau-data-api-mcp](https://github.com/uscensusbureau/us-census-bureau-data-api-mcp) | US Census Bureau | 106 stars, 32 forks, 0 commits, last push 2026-03-13 | Local: clone, Docker, seed a local database | Census API key; API plus local database | [A Feb 2026 article says it does not yet cover all Census data](https://www.paubox.com/blog/feds-adopt-open-source-protocol-to-connect-ai-chatbots-with-public-data). High setup friction |
| [i-dot-ai/lex](https://github.com/i-dot-ai/lex) | UK government AI incubator | 77 stars, 33 forks, 0 commits | Live at `lex.lab.i.ai.gov.uk/mcp` with 13 tools | No auth; own hybrid semantic index of 8.4M+ documents | README: "experimental… should not be used as a production dependency". Case law is "temporarily disabled pending TNA licence" |
| [i-dot-ai/parliament-mcp](https://github.com/i-dot-ai/parliament-mcp) | UK government AI incubator | 31 stars, 18 forks, 0 commits | 13 tools, including Hansard search and committees. Self-hosted | API data loaded into Qdrant | [Press links i.AI's Parlex tool with Parliament data](https://civictech.guide/projects/parlex-and-lex) (search excerpt, not opened). No usage figures |
| eSankhyiki MCP (India NSO) | [Reported in a PIB release as a beta launched 6 Feb 2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2224472&reg=3&lang=2) | n/a | Not verified | Not verified | The PIB page returned 403 to the fetcher, so this rests on a search excerpt only |
| [AgID/ckan-mcp-server](https://github.com/AgID/ckan-mcp-server) | Italy's digital agency; a fork of the community onData project | 1 star, last push 2026-10-28 | Same tool family as onData (below) | Same | [onData's README says AgID reused the project](https://github.com/ondata/ckan-mcp-server). An official body adopted a community server rather than building one |
| [GSA MCP hackathon](https://www.gsa.gov/artificial-intelligence/ai-community-of-practice/events-and-training/2026-ai-hackathon) | US GSA; runs Sep–Nov 2026, submissions due Nov 20 | n/a | Sandbox prototypes on public data; not publicly deployed | n/a | Open to federal through local .gov staff. No results published yet |

**City and local government decisions (the closest comparables)**

None of these is published by a city government.

| Server | Operator | Metrics | Tools, hosting, auth | Backend | Evidence |
|---|---|---|---|---|---|
| [OpenCouncil MCP](https://opencouncil.gr/mcp) | Schema Labs (Greek non-profit); [schemalabz/opencouncil](https://github.com/schemalabz/opencouncil) | 71 stars, 32 forks, 22 contributors, 100+ commits | Live, anonymous, 15 tools, including `search`, `list_hot_subjects`, `list_nearby_subjects`, `get_subject_transcript` | Own transcripts, LLM-extracted subjects | The closest overall match. Has a one-click Claude/ChatGPT setup page in Greek. No MCP usage figures |
| [OpenCityRecord](https://github.com/OpenCityUSA/opencityrecord-mcp) | OpenCity Record (US, commercial, beta) | 0 stars, repo created 2026-10-21 | `mcp.opencityrecord.org/mcp`, OAuth 2.1 (401 unauthenticated). Listed in the [official registry](https://registry.modelcontextprotocol.io/v0/servers?search=opencity) as `org.opencityrecord/opencity` | Own index: transcripts, votes, documents; 340+ cities/counties in 14 states | [Tiers from $0 (1 city) to $499/month](https://opencityrecord.org/mcp). No user numbers. The README says members of the public and staff are never named |
| [Open Council Network](https://opencouncil.network/api/docs/getting-started) | OCN Technology Ltd (UK) | No public repo identified (not searched exhaustively) | `opencouncil.network/mcp`, Bearer token (401 unauthenticated); proxies its JSON API | Own processing of council agendas, minutes, webcasts | [£249–£549/month, Enterprise on application](https://opencouncil.network/api/pricing). Paid plans include commercial use. Council count and customers not stated |
| [Desinformationssystem (DIS)](https://github.com/1612elphi/desinformationssystem) | Individual; Karlsruhe only | 1 star, 1 fork, 95 commits, 1 contributor | Live at `dis.delphi.tools/mcp`, anonymous, 17 tools including `search_documents`, `search_votes`, `get_vorlage` | Daily scraper, PDF text, LLM enrichment, SQLite FTS5 | No adoption evidence. Architecturally the closest to this repository |
| [zurich-opendata-mcp](https://github.com/malkreide/zurich-opendata-mcp) | Individual; [presented on the City of Zurich site, which says the servers were developed independently](https://www.stadt-zuerich.ch/de/politik-und-verwaltung/statistik-und-daten/open-government-data/anwendungen/anwendungen-2026/ckan-mcp-server.html) | 8 stars, 5 forks, 50 commits; PyPI 286/month | 23 tools, including `zurich_strb_search` (council resolutions), `zurich_parliament_search`, `zurich_geo_features`. Stdio; a hosted instance is credited to Liip | Live API passthrough | City showcase listing is the main signal |
| [BetaNYC MCP tools](https://beta.nyc/ai-tools) | BetaNYC (civic non-profit) | [nyc-record-mcp](https://github.com/BetaNYC/nyc-record-mcp): 2 stars, npm 51/month. [New-York-City-Budget](https://github.com/BetaNYC/New-York-City-Budget): 19 stars, 6 forks | 7 npm packages, including `nyc-council-mcp` and `nyc-budget-mcp` | Mostly API passthrough; budget data "checked by BetaNYC" | The page names no users or usage figures |
| [Catalyst Labs city-council transcripts](https://github.com/catalyst-labs-dev/catalyst-labs-mcp) | Commercial, via Apify | 0 stars, created 2026-10-18 | Remote through Apify; OAuth or token; $0.008 per audio minute | Own transcripts. Iowa lookup: 82 governments, 21,097 votes, self-reported 0.45% audited error | Self-reported benchmarks only |
| [jadu/modgov-mcp-server](https://github.com/jadu/modgov-mcp-server) | Jadu (UK); Modern.gov sites | 1 star, last push 2025-12-22 | Passthrough to the modgov API | Councillors, committees, meetings | No adoption evidence |
| [MunicipalMCP](https://github.com/Skatterbrainz/MunicipalMCP) | Individual; Municode | 6 stars, 0 forks, a single day of pushes (2025-12-04) | "Unofficial Municode API" | Passthrough | Abandoned or demo |
| [oparl-mcp-server](https://github.com/jtwolfe/oparl-mcp-server) | Individual; German OParl | 2 stars, 0 commits | README: "requires additional validation and testing" | Passthrough | Demo |

**Finland**

No official Finnish MCP server was found. GitHub search for `mcp ahjo` returned nothing, and `org:City-of-Helsinki mcp` returned nothing. The official registry returned nothing for `ahjo`, `finlex` or `eduskunta`.

| Server | Metrics | Scope and design | Status |
|---|---|---|---|
| [trotor/aura](https://github.com/trotor/aura) (Futuai Oy) | 8 stars, 2 forks, 100+ commits, 1 contributor | Live at `aura.futuai.fi/mcp`, anonymous, 8 tools. Metadata index in SQLite with Finnish inflection-aware search; `query_source` fetches rows live. 13,300+ datasets, 46 sources, 36 municipal map services | Most serious Finnish civic MCP. No usage numbers. Open core with a Pro layer |
| [MagnusKolsjo/mcp-for-eduskunta-finlex](https://github.com/MagnusKolsjo/mcp-for-eduskunta-finlex) | 0 stars, 36 commits, AGPL | 10 `fi_` tools. Live Eduskunta API plus local Finlex with FTS and pgvector. Initial sync "can take several days" | Actively built, no adoption evidence, self-host only |
| [matematicsolutions/fi-eli-mcp](https://github.com/matematicsolutions/fi-eli-mcp) | 1 star, 9 commits; PyPI 186/month; [PulseMCP estimate: 5.7k total, 165 this week, rank #4,639](https://www.pulsemcp.com/servers/matematicsolutions-fi-eli-mcp) | Finlex open-data API, ELI identifiers, verifiable citations; no key | Light and active. PulseMCP counts are its own estimates |
| [Ansvar-Systems/Finnish-law-mcp](https://github.com/Ansvar-Systems/Finnish-law-mcp) | 0 stars, 1 fork, **archived**, last push 2026-07-22 | Finnish legislation | Dead, yet [still listed on Glama](https://glama.ai/mcp/servers/Ansvar-Systems/Finnish-law-mcp) (per a search result; the listing was not opened) |
| [annasebedash-creator/finlex-mcp](https://github.com/annasebedash-creator/finlex-mcp), [NectiaAutomation/finlex-mcp-server](https://github.com/NectiaAutomation/finlex-mcp-server) | 0 stars; each created and last pushed on the same day (July 2026) | Local index; title search | One-shot demos |
| [SimonBerg255/finlex-mcp](https://github.com/SimonBerg255/finlex-mcp), [eduskunta-mcp](https://github.com/SimonBerg255/eduskunta-mcp), [helsinki-region-infoshare-mcp](https://github.com/SimonBerg255/helsinki-region-infoshare-mcp) | 0 stars; created 21–23 Mar 2026, last push 30 Mar 2026 | The HRI server wraps the Service Map, Linked Events and stat.hel.fi. **It has no decisions tools** | Dormant demos |
| [pipeworx-io/mcp-hilma](https://github.com/pipeworx-io/mcp-hilma), [mcp-helsinki-events](https://github.com/pipeworx-io/mcp-helsinki-events) | 0 stars. The Pipeworx account has 1,929 public repositories | Hilma procurement notices; Helsinki events. README: "independent, unofficial" | Mass-produced gateway wrappers; no evidence of individual use |
| [itulo/eu-nordic-open-data-mcp](https://github.com/itulo/eu-nordic-open-data-mcp) | 0 stars, created 2026-10-27 | TED, PRH, Brreg and others | Too new to judge |
| [markusl/statfin-mcp](https://github.com/markusl/statfin-mcp) | 12 stars, 2 forks, 0 commits | Statistics Finland | Quiet since June 2026 |
| [akunikkola/claude-for-legal-finland](https://github.com/akunikkola/claude-for-legal-finland) | 115 stars, 10 forks, 3 commits | Claude skills and plugins for Finnish legal work | Highest-starred Finnish legal AI repo found; primarily skills rather than a data service |
| [aikarjal/wilmai](https://github.com/aikarjal/wilmai) | 81 stars, 18 forks, 100+ commits | Wilma school system via MCP and CLI | Not government data, but the strongest Finnish MCP traction signal found. It targets a daily personal need |

**Other legislatures, law, courts and procurement**

| Server | Metrics | Notes |
|---|---|---|
| [Hack23/European-Parliament-MCP-Server](https://github.com/Hack23/European-Parliament-MCP-Server) | 30 stars, 9 forks, 100+ commits; npm 7,938/month | Community, not an EU product. Highest npm count in this set |
| [cyanheads](https://github.com/cyanheads/congressgov-mcp-server) portfolio: [Congress.gov](https://github.com/cyanheads/congressgov-mcp-server), [EUR-Lex](https://github.com/cyanheads/eur-lex-mcp-server), [Socrata](https://github.com/cyanheads/socrata-mcp-server), [CourtListener](https://github.com/cyanheads/courtlistener-mcp-server), [Sweden](https://github.com/cyanheads/sweden-parliament-mcp-server) | 1–11 stars; npm: EUR-Lex 2,868, Congress 1,598, Socrata 1,344, CourtListener 1,092 | One developer with a shared template, offering stdio plus hosted HTTP. Downloads are high relative to stars |
| [lzinga/us-gov-open-data-mcp](https://github.com/lzinga/us-gov-open-data-mcp) | 112 stars, 25 forks, 95 commits; npm 2,097/month | 40+ US APIs, 250+ tools |
| [ondata/ckan-mcp-server](https://github.com/ondata/ckan-mcp-server) | 59 stars, 15 forks, 100+ commits; npm 3,676/month | Live, 20 tools, works on any CKAN portal, hosted on Cloudflare Workers with a 100k/day shared quota. Reused by AgID and listed by Zurich. **Evidence-backed community success** |
| [jonashertner/opencaselaw](https://github.com/jonashertner/opencaselaw) | 76 stars, 16 forks, 100+ commits | Live, anonymous, 42 tools. 1M+ Swiss decisions. Offers MCP, REST, CLI and Parquet, with CC0 data. Own corpus and citation graph |
| [ReyemTech/mcp-canada](https://github.com/ReyemTech/mcp-canada) | 61 stars, 9 forks, 21 commits | 266 bilingual tools, including 2 municipal sources |
| [amurshak/congressMCP](https://github.com/amurshak/congressMCP) | 36 stars, 11 forks, 24 commits | Congress data, with a [commercial hosted site](https://congressmcp.lawgiver.ai) |
| [isakskogstad/Riksdag-Regering-MCP](https://github.com/isakskogstad/Riksdag-Regering-MCP) | 31 stars, 5 forks, 0 commits; npm 199/month | Swedish parliament and government; quiet since May 2026 |
| [hollobit/assembly-api-mcp](https://github.com/hollobit/assembly-api-mcp) | 94 stars, 33 forks, 0 commits | Korean National Assembly, 276+ APIs; quiet since May 2026 |
| [saidsurucu/ihale-mcp](https://github.com/saidsurucu/ihale-mcp) | 110 stars, 16 forks, 10 commits | Turkish tenders; niche, active |
| [Licinexus/licinexus-mcp](https://github.com/Licinexus/licinexus-mcp) | 81 stars, 40 forks, 0 commits | Brazilian procurement, company-maintained |
| [1102tools-dev/federal-contracting-mcps](https://github.com/1102tools-dev/federal-contracting-mcps), [blencorp/capture-mcp-server](https://github.com/blencorp/capture-mcp-server) | 28 stars, 100+ commits; 35 stars, 23 commits | US procurement; a professional audience with a clear job to do |
| [npstorey/civic-ai-tools](https://github.com/npstorey/civic-ai-tools) | 47 stars, 18 forks, 100+ commits | NYC Open Data and Data Commons starter, aimed at civic users |

**Abandoned or inactive open-data servers (evidence of decay)**

| Server | Metrics | Status |
|---|---|---|
| [OpenDataMCP/OpenDataMCP](https://github.com/OpenDataMCP/OpenDataMCP) | 156 stars, 22 forks | Last push 2024-12-20, 1 contributor |
| [melaodoidao/datagov-mcp-server](https://github.com/melaodoidao/datagov-mcp-server) | 20 stars, 5 forks | Last push 2025-04-09 |
| [AshwinSundar/congress_gov_mcp](https://github.com/AshwinSundar/congress_gov_mcp) | 19 stars, 5 forks | Last push 2025-06-30 |
| [bsmi021/mcp-congress_gov_server](https://github.com/bsmi021/mcp-congress_gov_server) | 8 stars, 2 forks | Last push 2025-06-01 |
| [r-huijts/opentk-mcp](https://github.com/r-huijts/opentk-mcp) | 23 stars, 4 forks | Last push 2025-10-30 |
| [mcp-open-data-hk](https://github.com/mcp-open-data-hk/mcp-open-data-hk) | 8 stars, 7 forks; PyPI 25/month | Last push 2025-08-14 |
| [tifa365/berlin-opendata-mcp](https://github.com/tifa365/berlin-opendata-mcp) | 5 stars, 1 fork | One day of pushes (2026-02-28) |

### Inferences
- Official publication is rare and concentrated at national level. Finland, and city government generally, is a gap rather than a crowded field.
- OpenCouncil.gr's MCP, OpenCityRecord and Open Council Network were all live or authenticated services within the same period. That suggests municipal-decisions MCP is an emerging product category in late 2026, not a settled one. None of them publishes MCP traction data.
- The official registry is not a usable success signal. A search for `datagouv` and `data.gouv` found only the unofficial Pipeworx entry and not the official server. Conversely, registry search also returned pay-per-call "municipal notices" endpoints with no visible provenance.

### Gaps
- Registry search is keyword-based, so absence from a result does not prove absence from the registry.
- Could not determine whether any government endorses or uses MagnusKolsjo's, Matematic's or Aura's Finnish servers.
- The Hilma and Helsinki-events Pipeworx servers were checked only by README or repo metadata, not by calling them.

## What evidence of success exists, and which projects are abandoned or demos?

### Takeaway
Only a few implementations have evidence beyond stars. The strongest is data.gouv.fr, followed by onData's CKAN server. Nobody publishes actual call volumes, so a claim of "success" here means attention and maintenance, not proven user value.

### Cited Findings

**Tier 1: strong, multi-signal evidence**
- data.gouv.fr: official, 1,604 stars, [press coverage and overload at launch](https://www.banquedesterritoires.fr/datagouv-facilite-lacces-des-ia-generatives-aux-donnees-publiques), still maintained — [repo](https://github.com/datagouv/datagouv-mcp). The same article reports limits: access mainly for advanced users, and slowness and errors on a roughly 900,000-row file.

**Tier 2: credible, with at least one independent signal**
- onData CKAN: AgID reuse, a City of Zurich listing, 3,676 npm downloads a month — [repo](https://github.com/ondata/ckan-mcp-server); [Zurich page](https://www.stadt-zuerich.ch/de/politik-und-verwaltung/statistik-und-daten/open-government-data/anwendungen/anwendungen-2026/ckan-mcp-server.html).
- i.AI Lex: government-run and live, but self-described as experimental — [repo](https://github.com/i-dot-ai/lex).
- OpenCouncil.gr: [€100,000 foundation donation in Nov 2024](https://schemalabs.substack.com/p/funds-product-motives?open=false); [an account of ten municipalities and over a million residents](https://app.innovationinpolitics.eu/?p=55794) (search excerpt, self-reported, not opened); 22 contributors — [repo](https://github.com/schemalabz/opencouncil).
- US-gov-open-data, OpenCaseLaw, Hack23 and the cyanheads portfolio: sustained commits plus downloads or forks, per the tables above. None shows named users.

**Tier 3: real and maintained, but no adoption evidence**
- Aura, DIS, OpenCityRecord, Open Council Network, Zurich, fi-eli-mcp, MagnusKolsjo (tables above).

**Tier 4: official but stale or high-friction**
- Census Bureau server: 0 commits since August, last push March 2026 — [repo](https://github.com/uscensusbureau/us-census-bureau-data-api-mcp).

**Tier 5: abandoned or demos**
- See the abandoned table above, plus MunicipalMCP, the SimonBerg255 trio and the archived Ansvar Finnish server.
- [OpenDataMCP](https://github.com/OpenDataMCP/OpenDataMCP) shows that 156 stars can sit on a project with no pushes for nearly two years.

**Suspect or non-comparable numbers**
- [DevnorsAI/devnors-data-mcp](https://github.com/DevnorsAI/devnors-data-mcp) has 674 stars and 3 forks, which is an unusual ratio. It was excluded as unreliable.
- [jjsantos01/qgis_mcp](https://github.com/jjsantos01/qgis_mcp) (1,145 stars) is a desktop GIS bridge, not a civic data service.
- The search results also contain high-star, unrelated repositories that merely mention MCP.

### Inferences
- A star count mainly reflects launch attention. Data.gouv combines a government brand with a large national catalogue and a zero-setup endpoint, and it dwarfs every municipal project. That comparison cannot be transferred to a single-city dataset.
- Downloads and stars diverge. `european-parliament-mcp-server` has 7,938 npm downloads a month and 30 stars, and `@cyanheads/eur-lex-mcp-server` has 2,868 and 11. Neither figure separates humans from automation.
- For planning purposes, a realistic early target for a single-city Finnish service is the Tier 3 range, not data.gouv's numbers. That is a judgement, not a measured baseline.

### Gaps
- No server publishes request volumes, unique clients or retention. Hosted endpoints cannot be measured from outside, including data.gouv, Aura and OpenCouncil.
- PulseMCP visitor counts were sampled only for a few servers. PulseMCP describes them as estimates. Glama and Smithery popularity data was not collected systematically.
- I found no independent evaluation of answer quality for any municipal server.

## What do they expose, and how are they hosted and backed?

### Takeaway
Three architectures recur: live API passthrough, a metadata index plus live fetch, and an owned corpus. Decision-data servers almost always need the third, because the source material is PDFs, video or web pages rather than clean APIs. Hosted Streamable HTTP is the common way to reach non-developers. Anonymous access is common for public-benefit servers, and OAuth or API keys for commercial ones.

### Cited Findings

**Architecture patterns**

| Pattern | Examples | Consequence |
|---|---|---|
| Live API passthrough | [data.gouv.fr](https://github.com/datagouv/datagouv-mcp), [GovInfo](https://github.com/usgpo/api/blob/main/docs/mcp.md), [Zurich](https://github.com/malkreide/zurich-opendata-mcp), [CKAN](https://github.com/ondata/ckan-mcp-server) | Cheap and fresh, but limited by what the upstream search can do |
| Metadata index plus live query | [Aura](https://github.com/trotor/aura) | Finnish-language discovery; rows fetched at query time; provenance attached to the answer |
| Owned corpus, FTS or vector search | [DIS](https://github.com/1612elphi/desinformationssystem), [OpenCouncil](https://github.com/schemalabz/opencouncil), [Lex](https://github.com/i-dot-ai/lex), [OpenCaseLaw](https://github.com/jonashertner/opencaselaw), [parliament-mcp](https://github.com/i-dot-ai/parliament-mcp) | Better search and enrichment, but carries pipeline, licensing and hosting costs |
| Hybrid | [mcp-for-eduskunta-finlex](https://github.com/MagnusKolsjo/mcp-for-eduskunta-finlex) | Live for current data, local for full text; multi-day initial sync |

**Tool-surface examples**
- Small: GovInfo has 2 tools. Aura's public profile is described as five intent-level tools plus three added facts tools (8 live), with instruction text under 1,500 characters — [Aura README](https://github.com/trotor/aura).
- Medium, domain-object shape: OpenCouncil has 15, including `get_more_tools`, which suggests deferred tool disclosure. DIS has 17 (committees, meetings, people, documents, votes, speeches).
- Very large: mcp-canada has 266, us-gov-open-data has 250+, OpenCaseLaw has 42.

**Response-design features worth noting**
- Aura returns structured output against a published `outputSchema`, with `provenance` (source, exact query URL, licence, retrieval time), `next_actions`, and `error.hint` with a corrected call — [README](https://github.com/trotor/aura).
- OpenCaseLaw has tools named `check_claim_support` and `attest_response` — live `tools/list` on [mcp.opencaselaw.ch](https://github.com/jonashertner/opencaselaw).
- OpenCityRecord links answers to the meeting page, video timestamp or minutes motion — [README](https://github.com/OpenCityUSA/opencityrecord-mcp).
- DIS treats the official PDF as authoritative: a live re-parse never overwrites a PDF-sourced vote — [README](https://github.com/1612elphi/desinformationssystem).

**Auth and pricing**

| Model | Examples |
|---|---|
| Anonymous, free | data.gouv.fr, Lex, Aura, DIS, OpenCouncil, CKAN hosted, OpenCaseLaw (all live-tested) |
| API key to a free service | [GovInfo](https://github.com/usgpo/api/blob/main/docs/mcp.md), [Census](https://github.com/uscensusbureau/us-census-bureau-data-api-mcp) |
| OAuth, consumer-style tiers | [OpenCityRecord, $0–$499/month](https://opencityrecord.org/mcp). [A directory listing says the beta is free through 1 Jan 2027](https://mcpservers.org/servers/opencityrecord-org-mcp), which differs from the vendor's page (a 30-day trial) |
| B2B API token | [Open Council Network, £249–£549/month and up](https://opencouncil.network/api/pricing) |
| Per-use marketplace | [Catalyst Labs on Apify](https://github.com/catalyst-labs-dev/catalyst-labs-mcp) |

### Inferences
- This repository already resembles the owned-corpus pattern: a geocoded JSON dataset built by scraping. Passthrough designs would not reproduce its value, since its heuristics, drawing selection and geocoding are the product.
- A small domain-object tool set in the style of OpenCouncil and DIS fits better than per-endpoint wrapping.
- Static JSON plus SQLite FTS is a proven low-cost base, since both DIS and Aura use SQLite. Vector search does not appear to be a precondition for usefulness, though no comparison was found.

### Gaps
- Hosting costs were not published by any project. Only onData's hosted Workers quota is stated.
- I did not call the tools to compare answer quality or response size; only `tools/list` was sampled, plus two Aura searches.

## Which non-MCP civic-tech analogues show demand and sustainability, and what happened to those that failed?

### Takeaway
Demand is real but pays unevenly. Paying customers have tended to be developers, other private clients and municipalities, not residents. Long-lived projects have a host institution or fiscal sponsor. Helsinki's own decision API, OpenAhjo, was closed, and no replacement date is available, while a Finnish service of unknown operator (Kotihiiri) already covers 55 municipalities.

### Cited Findings

**Finland**
- **OpenAhjo.** [The City-of-Helsinki/openahjo repo](https://github.com/City-of-Helsinki/openahjo) is archived (30 stars, 9 forks, created 2013, last push 2022-02-15). An [Avoindata note dated 12/2024](https://www.avoindata.fi/data/en_GB/dataset/4d992f0d-47a5-4645-aaaa-e5f1316bfe40) says the API "launched in 2015, has reached the end of its technical lifecycle and has been closed". A replacement is described as planned, with no date estimate. These notes were read as search excerpts only, because the catalogue pages returned 403 or 404 to direct fetches.
  - Date conflict: the note says 2015, but the repo dates from 2013 and [Forum Virium press covers an award for the interface](https://forumvirium.fi/en/the-city-of-helsinkis-open-decision-making-interface-wins-an-award/).
  - [dev.hel.fi/apis/openahjo](https://dev.hel.fi/apis/openahjo) refused connections on 2026-11-02. A search excerpt of the old page still described OpenAhjo as the way to access decision data.
  - The citizen site is alive: [paatokset.hel.fi](https://paatokset.hel.fi/en) answers, and [City-of-Helsinki/helsinki-paatokset](https://github.com/City-of-Helsinki/helsinki-paatokset) was pushed on 2026-10-30.
- **[Kotihiiri](https://kotihiiri.eu/).** Tracks meetings, votes and items in 55 municipalities: 4,210 meetings, 58,847 items, 2,591 votes. Refreshed weekly, links to originals, CC BY 4.0, no cookies. A further 41 municipalities are queued, 28 of them "awaiting permission". No API or MCP is mentioned on the page. Operator not named. **The closest Finnish neighbour to this project**, and it covers Helsinki.
- **[Kerro kantasi](https://github.com/City-of-Helsinki/kerrokantasi).** City-run: 8 stars, 15 forks, 38 contributors, 83 commits.
- **OmaStadi.** Helsinki's [participatory budgeting](https://civictech.guide/listing/omastadi) runs on Decidim, with [€10 million in the 2025 round](https://www.hel.fi/en/news/omastadi-makes-helsinki-better-do-you-know-what-participatory-budgeting-is) (search excerpt).
- **"Politiikkaradar".** No service with this name was found in Finnish or English searches.

**Sustained or commercial**

| Project | Evidence | Who pays or sustains it |
|---|---|---|
| [Hamlet](https://www.niemanlab.org/2026/01/highlighting-the-funniest-moments-this-startup-aims-to-bring-public-meetings-into-the-tiktok-era/) | $10M VC, 12 staff, "over a dozen clients", revenue in the "hundreds of thousands", not profitable. Figures as of Jan 2026 | Mostly real-estate developers, also data-centre developers, retailers and a PAC. Saratoga is its only government customer |
| [CivicBand](https://civic.band/) | 1,235 municipalities, 15.6M pages. An [earlier Open Collective snapshot said 700+ and 8M](https://opencollective.com/civicband) | Raft Foundation, donations, Fastly's Fast Forward. Pipelines are public ([clerk](https://github.com/civicband/clerk), 3 stars) and a pro product exists ([civic-observer](https://github.com/civicband/civic-observer)). No MCP mentioned on the site |
| [OpenCouncil (Schema Labs)](https://schemalabs.substack.com/p/funds-product-motives?open=false) | €100k donation and €5k prize (Jan 2025 post); active development | Non-profit owning a company that sells to municipalities; "steward ownership" |
| [Councilmatic (DataMade)](https://github.com/datamade/chi-councilmatic) | 33 stars, 16 forks, 13 contributors, 10 commits, repo dating from 2015. [NYC's Council took it on as an official site](https://ppolitics.medium.com/councilmatic-is-now-an-official-nyc-council-website-e6ddc542fe73) (search excerpt) | Civic-tech consultancy with client deployments. The [older open-city repo is deprecated](https://github.com/open-city/councilmatic), and [codeforamerica/councilmatic](https://github.com/codeforamerica/councilmatic) last pushed in 2015 |
| [Decidim](https://github.com/decidim/decidim) | 1,843 stars, 497 forks, 100+ contributors, 100+ commits | Institutional adopters; a participation platform rather than a data aggregator |
| [LocalLens](https://www.niemanlab.org/2025/03/local-newsrooms-are-using-ai-to-listen-in-on-public-meetings/), [Civic Sunlight](https://civicsunlight.ai/about/) | Newsroom use, e.g. [Chalkbeat monitoring about 80 school districts](https://www.niemanlab.org/2025/03/local-newsrooms-are-using-ai-to-listen-in-on-public-meetings/) (search excerpt) | Newsrooms; subscriber numbers not found |
| [citymeetings.nyc](https://citymeetings.nyc/) | [Self-reported 10,000+ visits a month, with government, media, advocacy and lobbying users](https://www.cityandstateny.com/power-lists/2025/02/whos-who-emerging-tech/403101/) (older source, search excerpt) | Solo founder with human review. Latest meeting visible on the fetched page: 7 Jan 2026, so current activity is unconfirmed |

**Declining or failed**

| Project | Evidence |
|---|---|
| [Council Data Project](https://github.com/CouncilDataProject/cdp-backend) | cdp-backend 25 stars, 27 forks, 0 commits, last push 2026-02-11. City instance repos such as [Boston](https://github.com/CouncilDataProject/boston) last pushed 2025-09-08. Not archived, but activity has clearly fallen |
| [OParl](https://github.com/OParl/spec) | Spec repo last pushed 2020-09-17. [A third-party blog counts 120+ German systems in the OParl registry](https://flowmcp.github.io/blog/2026-06-oparl-council-data/), unverified. The same post lists limits: no full-text title search, no date sorting. [DIS abandoned OParl for HTML scraping at Karlsruhe](https://github.com/1612elphi/desinformationssystem) because only `system` and `bodies` respond and they rate-limit |
| [Meine Stadt Transparent](https://github.com/meine-stadt-transparent/meine-stadt-transparent) | **Archived**, 46 stars, last push 2023-07-10 |
| Hamlet's public channel | [164 TikTok followers and 121 YouTube subscribers at the time of the Nieman article](https://www.niemanlab.org/2026/01/highlighting-the-funniest-moments-this-startup-aims-to-bring-public-meetings-into-the-tiktok-era/). Weak resident pull, as measured by that channel |

**Accuracy risks**
- [A councillor's blog criticised a Hamlet-derived article republished by Bridge Michigan as riddled with inaccuracies](https://a2elnel.com/post/when-ai-pitches-propaganda-about-ann-arbor-politics/) (search excerpt; a single critic's account).
- [Early Civic Sunlight summaries contained factual errors, prompting human editorial oversight](https://en.wikipedia.org/wiki/Tom_Cochran_(technologist)) (search excerpt; Wikipedia).
- Citymeetings.nyc [relies on human review of AI output](https://vikramoberoi.com/posts/how-citymeetings-nyc-uses-ai-to-make-it-easy-to-navigate-city-council-meetings/) (search excerpt).

**Audience tension**
- Hamlet's founder: "you can't keep all three happy in building a business like this", meaning citizens, companies and government — [Nieman Lab](https://www.niemanlab.org/2026/01/highlighting-the-funniest-moments-this-startup-aims-to-bring-public-meetings-into-the-tiktok-era/).

### Inferences
- The OpenAhjo closure cuts both ways for this project. It creates the opening, because no public structured decision API appears to exist. It also shows the risk, since official interfaces can disappear, and this repository already depends on an undocumented proxy.
- Open standards did not solve municipal data access on their own. OParl's stale spec and Karlsruhe's non-working endpoint suggest that vendor implementations decide real availability.
- Resident interest appears weak as a revenue base. Schema Labs itself [names getting citizens interested as its main challenge](https://schemalabs.substack.com/p/funds-product-motives?open=false). The likelier sustained users are professionals: developers, journalists, consultants, officials.
- Kotihiiri's "awaiting permission" queue may indicate that some municipalities' terms or technical access need agreement. This should be checked before assuming free reuse, although Helsinki is already covered.

### Gaps
- Kotihiiri's operator, funding and traffic are unknown. Its open-data section could not be located (a guessed URL returned 404), and a search returned nothing.
- OpenCouncil's current municipality count and revenue, CivicBand's budget, and Decidim's number of adopting cities were not found.
- Exact OpenAhjo shutdown date, official announcement, and reason beyond "technical lifecycle" were not found. HRI's [Feb 2026 steering-group minutes](https://www.hel.fi/static/avoindata/dokumentit/ohjausryhma/HRI-ohry_030226_muistio.pdf) reportedly do not mention Ahjo (search summary; not read directly).
- No Nordic equivalent of Hamlet or a commercial Finnish decision-monitoring product was confirmed. A "Pöytäkirjavahti" tracker appeared in a Finnish search result at [datagorilla.fi](https://datagorilla.fi/paattajalista/kangasniemen-kunta-paatoksenteko/) but was not examined.

## Are there MCP servers for geospatial or urban-planning data, or that combine documents with location?

### Takeaway
Generic geospatial MCP is well established, and zoning or permit servers are multiplying, mostly as property due-diligence tools. Very few link civic decisions to places. OpenCouncil's `list_nearby_subjects` is the clearest example found, and no Finnish server connects plan decisions, drawings and locations.

### Cited Findings

**General geospatial**

| Server | Metrics | Notes |
|---|---|---|
| [jjsantos01/qgis_mcp](https://github.com/jjsantos01/qgis_mcp) | 1,145 stars, 190 forks, last push 2025-10-01 | QGIS desktop bridge; a tool-operation server, not a data service |
| [nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp) | 406 stars, 89 forks, last push 2026-10-17 | Same category, active |
| [jagan-shanmugam/open-streetmap-mcp](https://github.com/jagan-shanmugam/open-streetmap-mcp) | 231 stars, 53 forks, last push 2025-07-12 | Popular but inactive |
| [mahdin75/gis-mcp](https://github.com/mahdin75/gis-mcp) | 202 stars, 54 forks, 16 commits; PyPI 482/month | Geometry operations; active |
| [sparkgeo/geo-mcp-servers](https://github.com/sparkgeo/geo-mcp-servers) | 247 stars, 37 forks, 20 contributors, 100+ commits | Tracked catalogue with a "Parcels & property" category. A useful reference |
| [cyanheads/openstreetmap-mcp-server](https://github.com/cyanheads/openstreetmap-mcp-server) | 9 stars, 1 fork | Geocoding and Overpass |

**Planning, zoning and permits**

| Server | Metrics or scale | Design |
|---|---|---|
| [chirikuuka/mlit-geospatial-mcp](https://github.com/chirikuuka/mlit-geospatial-mcp) | 191 stars, 26 forks, 0 commits | Japan's real-estate information library API, including city-planning GIS and zoning layers. Personal account; not verified as official |
| [Pluia](https://pluia.fr/ia) | [Listed in sparkgeo's catalogue](https://github.com/sparkgeo/geo-mcp-servers) as commercial, added 2026-10-29 | French PLU zoning by address or parcel, "rules cited with the official PDF page". The strongest document-citing precedent, though unverified beyond the listing |
| [iarfhlaith/gaff-check](https://github.com/iarfhlaith/gaff-check) | 8 stars, 4 commits | Irish property due diligence: planning applications, zoning, flood. README: "Records and clearly labelled derived context — never invented certainty" |
| [mheryerznkanyan/yerevan-gis-mcp](https://github.com/mheryerznkanyan/yerevan-gis-mcp) | 8 stars, 17 commits | Wraps the Yerevan municipal ArcGIS portal, including parcels and zoning. Read-only, no key |
| [mindwear-capitian/local-austin-mcp](https://github.com/mindwear-capitian/local-austin-mcp) | 6 stars, 0 commits on default branch | Built by a real-estate broker; 41 tools; offers a `local-{city}-mcp` template |
| [ccedacero/nyc-property-intel](https://github.com/ccedacero/nyc-property-intel) | 7 stars, 53 commits | 20+ NYC datasets; hosted MCP plus web chat with 3 free queries |
| [PermitStack/permitstack-mcp](https://github.com/PermitStack/permitstack-mcp) | 1 star; self-reported 119M+ permits in 8,000+ US cities | API key; free tier 100 requests a day |
| [ZoningSignal](https://registry.modelcontextprotocol.io/v0/servers?search=zoningsignal) | Registry: 25 Florida jurisdictions | Hosted planning and zoning records. Not opened beyond the registry entry |
| [BumiAtlas](https://github.com/BumiAtlas/malaysia-land-zoning-mcp) (Singapore, Malaysia, Indonesia, Thailand) | 0 stars on the Malaysia repo checked | Land lots and zoning; a registry-listed family |

**Documents combined with location**
- [OpenCouncil](https://opencouncil.gr/mcp) exposes `list_nearby_subjects`. Its [2025 post describes sessions organised around topics, each with a location, summary and speakers](https://schemalabs.substack.com/p/funds-product-motives?open=false). This is the clearest match to the idea of geocoded decisions.
- [OpenCityRecord](https://github.com/OpenCityUSA/opencityrecord-mcp) offers "issue and development-application timelines across meetings". No geographic tools were confirmed, because `tools/list` requires sign-in.
- [Zurich](https://github.com/malkreide/zurich-opendata-mcp) exposes council resolutions and geodata in the same server, but as separate tools with no join between them.
- [Aura](https://github.com/trotor/aura) accepts area names, postal codes and property IDs for geospatial queries. In a test on 2026-11-02, `find_data` for "Helsingin kaupungin päätökset Ahjo" returned an Oulu YouTube channel, Helsinki population data and Oulu's decision documents as the top three, with no Helsinki decision dataset among them. For "asemakaava Helsinki" it returned historical plan layers (1820, 1838, 1878).

### Inferences
- This project's combination of a decision, its drawing PDF, a location and the zoning archive looks uncommon. No comparable was found for Finland, and internationally only OpenCouncil and Pluia come close.
- Property due diligence is where zoning MCP servers are finding a job to do. That aligns with Hamlet's developer customers. It suggests real-estate and planning consultants as a plausible professional audience, though no MCP usage data confirms it.
- Spatial tools should reflect pin uncertainty. This repository's README warns that pins are approximate and deliberately spread. A "near this address" tool that ignores this would mislead more than a map does.

### Gaps
- No usage data exists for any zoning or permit server listed here.
- Pluia, ZoningSignal and Zoning Verdict were seen only through catalogues and registry listings; their tools were not verified.
- Finnish building-permit MCP was not found. The search was not exhaustive in Finnish terms such as `rakennusluvat`.

## What patterns distinguish the successful implementations from the failures?

### Takeaway
Across the evidence, the sustained projects share four traits: a publisher or institution with a reason to continue, a hosted zero-install path, a clear audience with a repeat need, and provenance back to the original record. Failures are typically one-developer wrappers around a single API, released once. These patterns come from observation of a small, biased sample, so they should be read as correlates and not causes.

### Cited Findings

**Patterns seen among stronger projects**
1. **Institutional or commercial backing.** Data.gouv.fr, i.AI, [Schema Labs](https://schemalabs.substack.com/p/funds-product-motives?open=false), [Raft Foundation for CivicBand](https://civic.band/), [Futuai for Aura](https://github.com/trotor/aura), [DataMade for Councilmatic](https://github.com/datamade/chi-councilmatic).
2. **Remote endpoint with one-line setup.** Data.gouv.fr's [README lists many clients and a hosted URL first](https://github.com/datagouv/datagouv-mcp). OpenCouncil has a [setup page written for non-developers](https://opencouncil.gr/mcp). onData recommends [hosted first, then local](https://github.com/ondata/ckan-mcp-server). In contrast, [Census needs Docker and a database seed](https://github.com/uscensusbureau/us-census-bureau-data-api-mcp), and [mcp-for-eduskunta-finlex needs a multi-day sync](https://github.com/MagnusKolsjo/mcp-for-eduskunta-finlex).
3. **Citations and provenance as a core feature.** [Aura](https://github.com/trotor/aura), [OpenCityRecord](https://github.com/OpenCityUSA/opencityrecord-mcp), [fi-eli-mcp](https://github.com/matematicsolutions/fi-eli-mcp), [Pluia](https://github.com/sparkgeo/geo-mcp-servers), [OpenCaseLaw](https://github.com/jonashertner/opencaselaw).
4. **Multiple surfaces, not only MCP.** OpenCaseLaw offers MCP, REST, CLI and Parquet. DIS, Aura and OpenCouncil all have a web UI. CivicBand, Kotihiiri and OpenCouncil are useful with no AI client at all.
5. **Generalisable reach.** [CKAN works across portals](https://github.com/ondata/ckan-mcp-server), which helps explain why AgID and Zurich both surfaced it. Most city-specific servers, by contrast, have under 10 stars. This is a real constraint for a single-city service.
6. **A paying or professional job to be done.** [Hamlet's developers](https://www.niemanlab.org/2026/01/highlighting-the-funniest-moments-this-startup-aims-to-bring-public-meetings-into-the-tiktok-era/), [Open Council Network's commercial users](https://opencouncil.network/api/pricing), [federal-contracting tools](https://github.com/1102tools-dev/federal-contracting-mcps).

**Patterns seen among failures**
1. **Thin, one-shot wrappers.** Same-day repos such as [annasebedash finlex-mcp](https://github.com/annasebedash-creator/finlex-mcp) and [berlin-opendata-mcp](https://github.com/tifa365/berlin-opendata-mcp).
2. **Early-hype stars without maintenance.** [OpenDataMCP](https://github.com/OpenDataMCP/OpenDataMCP), [open-streetmap-mcp](https://github.com/jagan-shanmugam/open-streetmap-mcp).
3. **Reliance on undocumented or unofficial upstreams.** [MunicipalMCP relies on an "unofficial Municode API"](https://github.com/Skatterbrainz/MunicipalMCP). This repository's README notes the same risk for itself.
4. **Multi-tenant self-hosting model.** [Council Data Project](https://github.com/CouncilDataProject/cookiecutter-cdp-deployment) depended on each city deployment, and those instances have gone quiet. CivicBand's central pipeline, by contrast, has kept growing.
5. **Standards without implementers.** [OParl](https://github.com/OParl/spec) and [its stalled tooling](https://github.com/meine-stadt-transparent/meine-stadt-transparent).
6. **Owner discontinuation.** [OpenAhjo](https://github.com/City-of-Helsinki/openahjo) and [Ansvar's Finnish server](https://github.com/Ansvar-Systems/Finnish-law-mcp) both ended despite a working product.

**Recurring risks, even among the strong projects**
- **Licensing:** [Lex disabled case law pending a licence from The National Archives](https://github.com/i-dot-ai/lex).
- **Impersonation:** [data.gouv warns that many servers falsely claim links to it](https://www.data.gouv.fr/posts/experimentation-autour-dun-serveur-mcp-pour-datagouv). The [Pipeworx listing](https://www.pulsemcp.com/servers/pipeworx-io-datagouv-fr) occupies that name in directories. Pipeworx's [Hilma README](https://github.com/pipeworx-io/mcp-hilma) carries a no-affiliation disclaimer; the data.gouv one was not read.
- **Hard-to-audit answers:** [data.gouv says this kind of setup is hard to audit, and that LLMs are not an official source](https://www.banquedesterritoires.fr/datagouv-facilite-lacces-des-ia-generatives-aux-donnees-publiques). [GovInfo likewise warns that LLM output needs quality assurance](https://github.com/usgpo/api/blob/main/docs/mcp.md).
- **Personal data:** [OpenCityRecord does not name members of the public or staff](https://github.com/OpenCityUSA/opencityrecord-mcp), and identifies only elected officials.
- **Directory noise:** [Glama still listing an archived server](https://glama.ai/mcp/servers/Ansvar-Systems/Finnish-law-mcp), and a [flood of generated Pipeworx repositories](https://github.com/pipeworx-io/mcp-hilma).

### Inferences

**What to copy**
- Aura's response envelope: provenance, licence, retrieval time, `next_actions`, error hints.
- OpenCouncil's domain tools, including a nearby-search tool, and its non-developer setup page.
- A public anonymous read-only endpoint, as with data.gouv, Lex, Aura and OpenCouncil.
- OpenCaseLaw's parallel bulk download alongside MCP. This repository already publishes JSON.
- DIS's rule that official documents override derived values. It suits this project's "hel.fi is the source of truth" stance.
- gaff-check's explicit labelling of records versus derived context, which fits the README's heuristic warnings: expose `location_method`, classification confidence and "drawing guess" fields.
- A small tool count, in line with Aura's concern for agent context.

**What to avoid**
- A per-endpoint wrapper with hundreds of tools.
- Requiring users to sync a database before first use.
- Depending on a single undocumented upstream without a cached copy and monitoring.
- Assuming that an official-sounding name or registry listing brings users.
- Relying on residents using AI clients as the only audience. [The Localtis article notes that access is limited to advanced users, often needing a paid subscription or technical setup](https://www.banquedesterritoires.fr/datagouv-facilite-lacces-des-ia-generatives-aux-donnees-publiques).
- Unattributed LLM summaries presented as facts, given the Hamlet and Civic Sunlight accuracy accounts.

**Likely implications for this project**
- A single-city, single-domain MCP should expect modest public metrics. Its differentiator is depth on plan decisions plus geography, which neither Kotihiiri (no MCP found) nor Aura (generic discovery) offers today.
- Coordinating with Kotihiiri, HRI or Aura could matter more than competing. Aura already has Finnish search and a hosted audience, and could possibly federate a decisions source. No contact or interest has been established, so this is only a hypothesis.
- Treat any "success" goal as something to instrument from day one, since no comparable offers a usable benchmark for calls or retained users.

### Gaps
- The sample suffers from survivorship and search bias. GitHub's ranking favours starred projects, and web search was US-based.
- No controlled comparison links any of these design choices to adoption. All patterns above are observational.
- No data was found on what share of civic MCP traffic is human-driven rather than automated.
- Not reviewed in depth: Smithery, mcp.so and the awesome-mcp-servers lists beyond incidental results; Norwegian and Danish municipal sources; Data Commons' MCP (only its mention in civic-ai-tools was seen).
