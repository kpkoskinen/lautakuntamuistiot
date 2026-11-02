# Who would use an MCP service over Helsinki planning decisions, for what, and on what evidence

Date of research: 2026-11-02. Local figures are my own read-only measurements on the repository (`data/plans_dataset.json`, `data/kerrokantasi_dataset.json`, generated 1 Nov 2026), and on live public sources where stated. They are labelled **[measured]**, and their source is the repository or the named endpoint. Rankings, effort sizes and costs are **[inference]**. No user research was done. No user quote or market figure here comes from a Helsinki user.

## Ranked use cases: who, what, and how far the data goes

### Takeaway
The best near-term fit is professional briefing and pipeline work (journalists, councillors' staff, consultants, developers), not residents. Nearly all of it depends on one cheap upgrade: storing the full decision text, which the source index already provides. Today's dataset is a good pointer to documents but a poor answer engine.

### Cited Findings: ranked table

Ranking is **[inference]**, weighing recurrence, willingness to pay, MCP fit and data distance. "Now" means what the present dataset can answer. Evidence is mostly foreign and indirect; see the next section.

| # | Use case and users | Example questions | Demand evidence | Now | Main missing piece |
|---|---|---|---|---|---|
| 1 | **Backgrounder on a place or case**: local journalists, councillors and assistants | "What has the committee decided on Lauttasaari since 2018, with links?" "Summarise the Hämeentie case." | Newsrooms pay for or build meeting monitoring (Hearst, Chalkbeat/LocalLens, Gazette), section below | **Partial, useful**: a name search finds candidates (Lauttasaari 36, Vallila 31, Kruununhaka 7 records) with links, but no content | Full text; City Board and Council steps |
| 2 | **Pipeline and competitor monitoring**: developers, brokers, construction suppliers | "Which residential zoning proposals in eastern Helsinki reached the Council this year, and how much floor area?" | Strongest willingness to pay: Hubexo subscriptions, Hamlet's developer customers, Barbour ABI | **Poor**: floor area appears in 0 of 905 stored records; adoption is not tracked | Full text extraction, status tracking, change feed |
| 3 | **Political accountability**: councillors, assistants, journalists, NGOs | "Where did the committee vote on a street plan? Who dissented?" "Which plans were tabled?" | BetaNYC's council tool covers votes, for councillors and journalists among others (no usage data) | **None**: votes and dissent are not stored | Full text, vote parsing, members |
| 4 | **Precedent search**: architects, planning and traffic consultants, lawyers | "How were heritage or noise issues handled in recent infill plans?" | Inference only; no direct evidence found | **Almost none**: "melu" matches 1 stored record, 242 with full text | Full text, reports and drawings |
| 5 | **Civic preparation of opinions**: neighbourhood associations, environmental NGOs | "What is on view in our district, and what was decided nearby before? Help draft a muistutus." | Associations and NGOs do file opinions (titles seen: Helvene, Tringa); the city already alerts | **Partial** for history; no display deadlines except Kerro kantasi `close_date` | Display periods, polygons, plain-language help |
| 6 | **Longitudinal research**: urban, political and data researchers | "How did plan volume change by district after the 2017 reorganisation?" | Inference; Helsinki participation research exists but says nothing about tools | **Partial**: type, year and committee counts work; stage is weak before 2017 | Bulk text export; **a dataset serves better than MCP** |
| 7 | **"What is planned near me?"**: residents, housing companies, property managers | "Is anything planned within 300 m of Vaasankatu 10?" | Highest volume abroad (PlanningAlerts, 169 230 alerts a week) but a charity, low willingness to pay | **Misleading**: see radius test below | Polygons, address search; **a website or alert serves better than MCP** |
| 8 | **Works coordination**: utilities, street contractors | "Which approved street plans touch this corridor?" | No evidence found | **Partial**: 366 approved street plans, but no schedule, extent or budget | Extents, works schedule; other sources |
| 9 | **Internal knowledge**: city officials | "Have we decided something similar?" | Saratoga and Palo Alto are Hamlet customers; citymeetings was hired by a city commission | **Weak**, and officials have the source systems | Full text; procurement route |

Groups in the question were merged: NGOs into 3 and 5; architects and consultants into 4; brokers into 2.

**What the people do today, by group.** Sourced facts are few:
- The city offers free channels: [Suunnitelmavahti](https://www.hel.fi/fi/uutiset/suunnittelu-ja-kaavoituskatsaus-esittelee-helsingin-ajankohtaiset-suunnitelmat) emails when plans go on view and announces resident meetings; the same page describes the annual Kaavoituskatsaus and `kartta.hel.fi/suunnitelmat`, which holds "kaavahankkeisiin liittyvät dokumentit, aikataulut ja yhteystiedot".
- [paatokset.hel.fi](https://paatokset.hel.fi/fi) offers decision search from 2017 and a PDF minutes archive for 2011–2023; the home page shows no alert, RSS, API or map search (home page only).
- Housing companies: cases show them filing written objections in display periods, e.g. [Turku](https://ah.turku.fi/kv/2023/0417004p/Images/2194616.pdf) and [Tampere](https://tampere.cloudnc.fi/download/noname/%7B72bfebdf-28d5-4d43-af29-b5534e63192b%7D/3647088) (seen through a search summary, not read in full; not Helsinki).
- Developers and suppliers: [Hubexo Finland's directory listing](https://www.fonecta.fi/profiili/hubexo-finland/4010557) describes a project information service with decision-makers' contacts. A related directory listing says data is collected through telephone interviews with developers. I saw both only through a search summary, and could not tie the interview claim to one exact page.
- **Cost to users: I found no sourced figure for any Finnish group.** See Gaps.

**How often a need arises [measured].** Located plan decisions run at 83–108 a year citywide since 2018. By name match: Lauttasaari 36 records, Vallila 31, Kruununhaka 7 across 14 years, or about 0.5–2.6 a year per district.

### Inferences
- Low per-district volume means a resident's need is episodic, triggered by one project. That argues against a paid resident product and for a free alert or lookup. Professionals who watch the whole city have the recurring need.
- Combining a location with content (case 1) is the most defensible offering: neither Suunnitelmavahti nor paatokset.hel.fi appears to answer "what has happened here, and why?" in one place. Not verified against `kartta.hel.fi/suunnitelmat`, which I did not inspect.
- Use case 2 has the money and an established rival. The likely entry is a complement to Hubexo-style data (earlier signal, decision text with citations), not a replacement.

### Gaps
- No interviews or surveys of Helsinki journalists, councillors, associations or developers. **The ranking is a hypothesis.** Five to ten short interviews would test it better than more desk research.
- No time or money cost was found for any group, and I have not estimated one.
- I found no study measuring how Finnish residents find planning decisions. The nearest are [Espoo's statement](https://www.espoo.fi/en/housing-and-building/city-planning/participation-part-city-planning) that participation takes time and understanding of the process, [a 1993 Ylistaro study](https://trid.trb.org/View/451061), [Wallin 2015](https://aluejaymparisto.journal.fi/article/download/64831/26061/74685) on Herttoniemi and [Ovaska's thesis](https://osuva.uwasa.fi/bitstream/10024/3865/1/osuva_6645.pdf) on Keski-Pasila (the last three via search summaries).
- The Helvene and Tringa opinions were seen as titles in search results only ([Helvene](https://helvene.yhdistysavain.fi/@Bin/1541716/Helveneen+lausunto+Hernesaaren+kaavasta+2023+12+18.pdf), [Tringa](https://tringa.fi/wp-content/uploads/2026/06/2026-mielipide-Gardenia-OAS.pdf)).

## Demand and willingness to pay in similar products

### Takeaway
People pay when planning information is a business input (project leads, government affairs, competitor tracking). Resident and civic services draw real use but depend on donations or volunteers. No source shows anyone paying specifically for MCP access to municipal decisions.

### Cited Findings

**Paid, professional**
- Hubexo (formerly Byggfakta Group): group [ARR of SEK 2 209 million, 85.1 % subscription revenue](https://financialreports.eu/filings/681099/content), from a search summary of its Q4 report, group-wide. It lists [1.3 m active projects and 50k customers](https://nee.hubexo.com/?p=11), not broken down by country.
- Hubexo Finland Oy: [2024 revenue "11 milj." and 64 staff](https://www.fonecta.fi/profiili/hubexo-finland/4010557), per a directory listing; currency not stated and the listing has oddities, so treat with caution. No Finnish subscriber count or price was found.
- Hamlet (US): [$10 m total funding](https://www.ai-market-watch.com/company/hamlet) per a profile that also mentions a $5 m seed without reconciling them. It names Saratoga, Palo Alto and Acres.com, and lists real-estate developers and data-centre operators as customers. No pricing or revenue. The site itself was unreachable (HTTP 429).
- Plural (legislative tracking): [free tier; Basic $3 500 a year; Premium from $10 000 a year](https://pluralpolicy.com/blog/video-plural-pricing-plans/). This is the clearest public price anchor, though for state and federal policy teams rather than municipal plans.
- Barbour ABI (UK leads): [custom pricing by enquiry](https://datarade.ai/data-products/barbour-abi-construction-project-leads-barbour-abi); subscriptions include [contact details](https://barbour-abi.com/products) (search summary). Contacts appear to be a large part of the value.
- FiscalNote: [no published price](https://www.g2.com/products/fiscalnote/pricing); it claims [coverage of over 16 000 local governments and school districts](https://business.mammothtimes.com/mammothtimes/article/bizwire-2024-12-17-fiscalnotes-ai-powered-local-legal-and-regulatory-coverage-hits-new-milestones-now-exceeds-5-million-policy-documents-in-its-proprietary-database-and-the-highest-number-of-tracked-localities-in-the-us) (press release, search summary).
- Quorum: [quote-only with modular tiers including Local](https://thegtmdirectory.com/tools/quorum/md) (third-party directory; weak source).
- Civic Eagle: only a [thin third-party listing](https://serchen.co.uk/company/civic-eagle) tying it to Plural. No price found.

**Civic, free or donation-funded**
- PlanningAlerts (Australia, run by a charity): ["This week": 169 230 email alerts received, 125 new sign-ups, 4 207 new applications, 18 new comments](https://www.planningalerts.org.au/), alongside "Without more monthly supporters, our library will close". It is the best public signal of large resident use and of weak resident funding at the same time.
- PlanningAlerts' commercial API: [a December 2023 agreement template shows up to 5 000 requests a day for commercial use including republishing, at $3 499 a month plus GST](https://www.oaf.org.au/wp-content/uploads/2024/03/202312-PlanningAlerts-API-Supply-Agreement.pdf). Currency is presumably AUD. It is a template, so it shows a price asked, not that anyone pays it.
- UK PlanIt: [one-person aggregator, 417 authorities (over 30 not up to date), about 20.8 million applications, 91 % mappable, API and CSV/JSON, funded by donation appeal](https://www.planit.org.uk/). Resellers wrap it: [Apify listings](https://apify.com/devon_gtme/uk-planning-applications-planit) were reported from $0.005 to $20 per 1 000 applications depending on seller (search summary, inconsistent), and one has an [MCP endpoint page](https://apify.com/devon_gtme/uk-planning-applications-planit/api/mcp). I saw no usage figures.
- citymeetings.nyc: one-person project, [hired by the Charter Revision Commission in 2025; has spoken to city offices and Bloomberg's data journalists](https://citymeetings.nyc/about/). It [went offline in June 2025 while the author focused on other work; about 100 people joined the newsletter meanwhile](https://buttondown.com/citymeetingsnyc/archive/citymeetingsnyc-happy-new-year-back-in-early-2026/). A warning about sustainability, and a small sign of latent interest.

**Newsrooms**
- Hearst's Assembly: [460 agencies tracked and over 10 000 meetings processed](https://www.inma.org/blogs/ideas/post.cfm/hearst-s-new-tool-harnesses-ai-to-expand-local-news-coverage-of-public-meetings) (self-reported, search summary; the page refused my fetch).
- Gazette's CivIQ: [council stories per publication per month rose from 1.2 to 6.5](https://newsinitiative.withgoogle.com/resources/stories/ai-brings-5x-boost-to-local-news/) (self-reported case study).
- Chalkbeat: [built its own tool, then set it aside for LocalLens, monitoring about 80 school districts in 30 states](https://niemanlab.org/2025/03/local-newsrooms-are-using-ai-to-listen-in-on-public-meetings). Both newsrooms in the piece require independent checks: "It is a tip". Findings were anecdotal, with no measured outcomes. Chalkbeat's experience suggests buying over building.
- [APM acquired LocalLens in November 2025](https://www.americanpublicmedia.org/blog/american-public-media-acquires-locallens-ai-tool-to-empower-journalists-nationwide) (search summary).

**Helsinki participation signal [measured, kerrokantasi.api.hel.fi]**
- The API lists 401 hearings. The first 100 returned total 20 774 comments, median 89, maximum 3 169. Page order was not checked, so this is not a random sample. It shows residents engage on planning issues, not that they want a data service.

### Inferences
- Much of the US value comes from transcribing long video meetings. Helsinki's decisions are already published as text, so the transcription moat does not apply; the barrier and the value are lower. This limits how far US products serve as evidence.
- Helsinki alone is a small market. Plural-level pricing ($3 500+ a year) is a stretch for one city's planning decisions. Credible routes are grants or public funding, a consultancy-led offer, or expansion to other Finnish cities. This needs testing.
- The rival for use case 2 is not another MCP server but a sales-enabled database with contacts, which this project does not have and should be careful about adding (GDPR).

### Gaps
- No evidence on Rakennuslehti project databases: searches found [only a general description](https://webcatalog.io/en/apps/rakennuslehti), no project product or price.
- I found no service that sends alerts from Ahjo decisions in Finland. Absence from search is not proof.
- Suunnitelmavahti subscriber counts were not found. A request to the city would answer this and be the best local demand figure.
- Dun & Bradstreet-style leads: nothing Finland-specific; Hubexo is the nearest match. No revenue or customer counts for Plural, Quorum or Hamlet.

## Would MCP beat a website, plain dataset or RAG chatbot?

### Takeaway
MCP suits a narrow group today: professionals already working in an AI assistant, who ask multi-step questions and want citations. For residents a website with alerts is better. For researchers a dataset or API is better. The sensible architecture is a plain API or dataset first, with MCP as a thin layer over it.

### Cited Findings
- [Stacklok's survey of senior technical leaders](https://stacklok.com/resources/state-of-mcp-in-software-2026/): nearly half of software companies use MCP in production, 19 % broadly; primary users are developers (80 %) and data analysts or scientists (68 %); security is the top obstacle (64 %). It is a vendor survey of software firms and says nothing about Finnish journalists or associations.
- Developer-side scale figures of [10 000+ servers and 97 m monthly SDK downloads](https://dev.to/gentic_news/mcp-hits-10k-servers-97m-monthly-sdk-downloads-by-may-2026-1jbk) are repeated widely by weak secondary sources, and measure developers rather than end users.
- Client access: Claude offers [custom connectors on all plans, with Free limited to one](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp). ChatGPT's rules are reported inconsistently by [third parties](https://peliqan.io/blog/chatgpt-mcp/), generally fuller on workspace plans; check OpenAI's own documentation.
- Civic MCP servers exist, and none I found publishes usage: [BetaNYC's council and budget tools](https://beta.nyc/ai-tools), aimed at "New Yorkers, journalists, researchers, community boards, and council members"; [Boston's open data server](https://glama.ai/mcp/servers/thealphacubicle/boston-core-mcp); [OpenCityRecord](https://mcpservers.org/servers/opencityrecord-org-mcp); [a Gloucester pilot](https://lobehub.com/mcp/gloucester-city-council-gcc-mcp-pilot); and [a generic Socrata connector](https://cdn.jsdelivr.net/gh/srobbin/opengov-mcp-server@main/README.md). Supply is well ahead of any shown demand.

### Inferences
| User | Better interface | Why |
|---|---|---|
| Residents, housing companies | **Website, map, email alert** | Episodic use; no assistant set-up; the city's Suunnitelmavahti already covers on-view alerts |
| Researchers | **Dataset or API** | Reproducible bulk analysis. MCP adds little |
| Developers, suppliers | **Feed or API into CRM**, MCP as a bonus | Their workflow is lists and alerts in existing tools |
| Journalists, assistants, consultants | **MCP is reasonable**, with a website for sources | Multi-step research with citations, mixing own notes and sources. Needs them to use such clients already (unmeasured) |
| Associations, NGOs | **Hosted chatbot or website**, MCP for technical volunteers | Drafting help is valuable, but set-up is a barrier |
| City officials | **Internal tool** through procurement | IT and security policy decide; not verified for Helsinki |

- MCP vs own RAG chatbot: MCP avoids building a chat interface and paying model costs, and users combine it with their other tools. A chatbot reaches people without an AI subscription and gives control over disclaimers. Exposing structured tools (filter by stage, place, date) should beat vector search alone for count and list questions, which RAG handles poorly.
- MCP has a specific risk here: the assistant may state a heuristic field as fact and drop the caveat. Tools should return confidence and source fields, and the service should never return "status: approved" without its basis.
- Candidly, the current dataset could be served through an MCP server in days, but as a thin search over excerpts it would add little beyond the existing map and paatokset.hel.fi search.

### Gaps
- No data on how many Finnish journalists, councillors' assistants or planners use MCP-capable clients. This is the largest unknown for the MCP choice specifically.
- No usage metrics for any civic MCP server. Their maintainers could be asked directly.

## What the current data can answer: field tests

### Takeaway
Coverage and links are solid; content is thin. Only 37 % of records have a meaningful summary, every one of them at most 320 characters, and the stored fields miss almost every topic a user would ask about. A parser bug accounts for much of the gap and is easy to fix.

### Cited Findings: all [measured]

**Decisions (`plans_dataset.json`, 1 727 records, 105 more unlocated)**
- Fields always present: committee, dm, asia_id, plan_type, heading, title, date, year, month, decision_url, location, lat, lon, geocode, stage. Partly present: map_url 1 581, summary 993, attachments 729.
- Type: asemakaava 775, katu 371, liikenne 306, puisto 218, muu kaava 57.
- Stage: proposal 827, approved 715, other 173, returned 12. Zoning: 628 of 775 are proposals. Traffic: 131 of 306 are `other`.
- Geocode: street 1 179, district 438, place 104, manual 6. Only 816 distinct coordinates exist.
- Committee: Kaupunkiympäristölautakunta 905, Kaupunkisuunnittelulautakunta 561, Yleisten töiden lautakunta 261. No City Board, Council or official-holder decisions.
- Newest decision in the data is 27 Oct 2026.

**Summary quality**
- 734 records have no summary, including all 624 from before 2017.
- Stored summaries are capped at 320 characters by `common.decision_fields`; median among all records is 141.
- **357 of the 993 summaries are not decision text.** They hold a boilerplate notice: "tullut nähtäväksi … MUUTOKSENHAKUKIELTO … Kuntalaki 136 §". All 357 are `proposal` records, 2017–2026.
- Likely cause (**[inference]** from the code and index text): these pages carry the text under an "Esitys" heading, and the parser's anchor on the word "Päätös" catches the later notice.
- That leaves **636 real summaries (37 % of records)**; 462 end in a truncation mark. From 2018 on, 537 of 874 (61 %) are real.

**Full text exists and is unused**
- The public Elasticsearch index that `scrape_decisions` already queries has `decision_content` and `decision_motion`. The scraper requests neither (`all_decisions` asks only for subject, URL, date, ids).
- For the 905 records of Kaupunkiympäristölautakunta I joined to it: median 984 characters of decision content and 7 277 of motion text, together about 25 times the 320-character cap. Empty: 0 and 2 records. All 905 joined. The other 90 paatokset-sourced records are the predecessor committees, which I did not pull.
- A sample of 23 decision pages, 2019 on: all had reasoning (perustelut) and appeal text; median about 20 000 characters of page text.

**Topic recall on those 905 records (stored fields vs full text)**

| Topic | Regex | Stored | Full text |
|---|---|---|---|
| Cycling | pyör | 7 | 498 |
| Trees | puu, puiden, puusto | 14 | 520 |
| Parking | pysäköin | 6 | 524 |
| Floor area, residents | k-m, kerrosala, asukas | 0 | 746 |
| Cost | euro, € | 0 | 775 |
| Noise | melu | 1 | 242 |
| Protection, demolition | suojel, purk | 7 | 428 |

These are rough matches. Full-text hits include passing mentions and false matches, so they show how much is out of reach, not how many are relevant answers.

**Votes and dissent**
- Decision content of 905 records: vote terms in 76 (8 %), dissent terms (eriäv, vastalause) in 4, tabling in 22, return in 15. Patterns are rough. Stored fields hold 0 for votes and dissent. Page sample: vote terms in 3 of 23, dissent in 1 of 23.
- Dissent is rare, and my pattern may miss wordings. A "who dissented" feature will have few results.

**Stage accuracy: a rough cross-check**
- From the opening of the decision text I derived an outcome with my own rough patterns; this is not ground truth.
- 12 labelled `returned`, but 31 show tabling or return: **19 tabled decisions are labelled `proposal`**, because the title contains "esitys" (e.g. 14 Nov 2017, 18 Sep 2018, 9 Oct 2018).
- All 453 classifiable `approved` records agreed, but the same word drives both tests, so this is weak support.
- 15 records labelled `proposal` read "hyväksyä … luonnoksen jatkosuunnittelun pohjaksi". The label is arguably right: my pattern misread them, which shows the wording trap either way.
- 130 proposal records could not be classified by my patterns.
- Before 2017 there is no text at all: 220 `approved` records rest on titles such as "…hyväksyminen". That is the agenda item's name, not the outcome. Tabled items would be mislabelled, and this cannot be checked from stored data.

**Status does not follow the case**
- The dataset keeps one record per `dm + asia_id + plan_type`, preferring the decision with a drawing over the latest (`better_decision`). Only 9 cases show more than one stage.
- 70 of 905 records have a later committee decision in the same case. Many are the same stage, so this is an upper bound on staleness within the committee.
- **Of 298 zoning proposal cases from 2017 on, 256 (86 %) also appear in City Board or Council decisions in the index, by case id.** The dataset still says only "proposal". Linking works, though I did not parse the outcomes or check date order. Some index URLs use a UUID rather than the case id, so this is probably a lower bound.

**Location: a test of radius search**
- I matched zoning records by plan number to the city's polygons of plans in force (WFS, 4 394 features). 655 matched. Distance from pin to polygon:

| Geocode | Records | Inside polygon | Median distance | Over 250 m | Over 500 m |
|---|---|---|---|---|---|
| street | 485 | 86 (18 %) | 71 m | 135 (28 %) | 64 (13 %) |
| district | 146 | 26 (18 %) | 295 m | 81 (55 %) | 47 (32 %) |
| place | 24 | 10 (42 %) | 5 m | 2 | 0 |
| **All** | 655 | 122 (19 %) | | 218 (33 %) | 111 (17 %) |

- Caveats: zoning only; only plans in force; the plan number is regexed, so the largest distances (up to 9.6 km) may be wrong matches. Pins here are the dataset's true coordinates, before map spreading, which adds more offset on the map.
- All 22 records located at Mannerheimintie share one coordinate. 815 of 1 179 street records share a coordinate with another.
- Plan number can be derived for 726 of 775 zoning records from the text, but it is not a field. 383 records contain a street-and-number pattern in stored text.

**Consultations (`kerrokantasi_dataset.json`, 185 records, 19 unlocated)**
- 165 are located by their own drawn area (reduced to centroid and `area_km`; polygon not stored). 163 have an abstract, median 278 characters, maximum 536. `close_date` is present on all, and 167 have drawings.
- Comments and comment counts are not stored. The asia_id is a slug such as `kk-hameentie`, with no link to decision cases.

**Drawings**
- 92 % of located decisions link a drawing (1 581 of 1 727, matching the README). Of 12 random drawing PDFs from 2018 on, all had a text layer, from 117 to 41 077 characters (median about 7 700); 4 had under 1 000. Text in a drawing is mostly labels. I did not check whether the longer ones are actually reports or evaluate how usable the text is.

### Inferences: what each use case gets today
- **1 Backgrounder:** works as a finder of documents with place, date and type filters, if the assistant then opens the links. It cannot explain why.
- **2 Pipeline:** can list recent zoning items by district but not size, use or adoption. Not sellable as is.
- **3 Accountability:** cannot be done.
- **4 Precedent:** cannot be done except by plan type and place.
- **5 Civic prep:** history is partly usable, and Kerro kantasi deadlines work. Statutory display periods for plans are absent.
- **6 Research:** counts by type, year and committee are fine. Trends across 2017 are confounded by changes in committees and source (and by zero summaries before it).
- **7 Near me:** give district-level answers only, with a warning.
- **8 Works:** a list of approved street plans by name; no timing.
- **9 Officials:** nothing they lack.

### Gaps
- `data/quality_sample.csv` is unreviewed, so type, drawing and location accuracy have no human measure. My cross-checks are not a substitute. Reviewing it would be cheap and necessary before any launch.
- Recall of the plan classifier against all relevant decisions was not measured. Kaupunkiympäristölautakunta subjects with plan-like words number 1 594, versus 1 459 processed URLs in `seen_decisions`; the exclude list explains an unmeasured part of this.

## Feature gap table

### Takeaway
A useful first release is about two to three weeks of work **[inference]**: fix the parser, store full text with citations, add the plan number and a City Board and Council join. Polygons for pending plans and address search come next. Alerts, vote extraction and PDF search come only if interviews support them.

### Cited Findings
What the code supports, checked in `lautakuntamuistiot/*.py` **[measured]**:
- There is no MCP server, API, search index, full-text store, radius or address function, or user alert.
- A grep for radius, haversine, RSS, subscribe and alert found only uMap cluster settings.
- "What changed" exists as `check_updates`, `update_report` and `data/update_log.md`, about map pins and for maintainers; it could seed a feed.
- `scrape_decisions --org` accepts any organisation name, but only the committees are run.
- Polygons exist only in the separate `scrape_zoning` output, which is not published in `data/`, and cover plans in force only.

Effort **[inference]**: S up to 2 days, M up to 2 weeks, L longer. Use-case numbers refer to the ranked table.

| Feature | Use cases | Effort | Data source | Status in code |
|---|---|---|---|---|
| Fix summary parser (Esitys vs Päätös); recompute stage | all | S | Existing pages or index | Bug: 357 records |
| Store full decision and motion text | 1, 2, 3, 4, 5, 9 | S | ES `decision_content`, `decision_motion` (undocumented proxy) | Available, not requested |
| Full-text search with cited passages | 1–5, 9 | M | Above, with Finnish stemming | None |
| MCP server (read-only tools, citations, confidence fields) | 1–5 | S–M | Dataset | None |
| Plan number as a field | 1, 2, 4, 5, 7 | S | Regex (726 of 775 zoning) | Not a field |
| City Board and Council decisions, case timeline | 1, 2, 3 | M | ES, by case id (256 of 298 link) | Possible via `--org`, needs a timeline model |
| Keep all decisions per case, not the best one | 1, 2, 3, 5 | S–M | Existing scrapers; change upsert key | Overwrites by design |
| Outcome from text, stated with its basis | 1, 2, 3, 6 | M | Full text; needs a labelled test set | Keyword heuristic |
| Pre-2017 text | 4, 6 | M–L | hela Paatostiedote pages and PDFs | Titles and attachments only |
| Votes and dissent extraction | 3 | M | Full text; few cases, 76 of 905 with vote terms | None |
| Councillor or member data | 3 | M | paatokset person search; source not assessed | None |
| Appeals and legal force | 2, 3, 7 | M–L | WFS `lainvoimaisuuspvm` for plans in force; other appeals not traced | Date read by `scrape_zoning`, not linked |
| Polygons for plans in force | 2, 5, 7, 8 | S–M | WFS (655 records matched) | Separate product |
| Polygons, schedules and documents for pending plans | 1, 2, 5, 7 | M, uncertain | `kartta.hel.fi/suunnitelmat`; API not assessed | None; **check first** |
| Address and radius search | 5, 7, 8 | M | Polygons plus address data; meaningless on pins alone | None |
| Display periods and objection deadlines | 5, 7 | M | Suunnitelmavahti, planning pages, notices; extraction not assessed | Only Kerro kantasi `close_date` |
| Change feed (RSS or JSON) | 2, 5 | S | `update_report` | Internal log |
| Email or webhook alerts by area or topic | 2, 5, 7 | M | Feed; personal data duties | None; overlaps Suunnitelmavahti |
| Kerro kantasi: stored polygons, comment counts, link to case | 1, 3, 5 | S–M | API; comments are CC BY-NC-SA | Centroid only, none |
| Comment text and analysis | 1, 3, 6 | M | API; licence limits commercial use | Deliberately not collected |
| Drawing and report PDF search | 2, 4, 8 | M–L | ahjojulkaisu, ptp.hel.fi; copyright may apply, so index with care | Links only |
| Official-holder decisions | 1, 2, 5, 8 | M | ES: e.g. Liikenne- ja katusuunnittelupäällikkö 1 403 decisions, 338 "suunnitelm" subjects; Maankäyttöjohtaja 1 256, including poikkeamishakemus | Not scraped |
| Other committees, permit division | 2, 7 | M | ES: lupajaosto 2 171; building permits may need other sources | Not scraped |
| Works schedules and budgets | 2, 8 | L | No source identified | None |
| Other cities | 2 | L | Case systems differ; not assessed | None |

Sources for this table are the repository and the live index [measured], and the [city's description of its map service](https://www.hel.fi/fi/uutiset/suunnittelu-ja-kaavoituskatsaus-esittelee-helsingin-ajankohtaiset-suunnitelmat).

**Availability notes**
- Index totals [measured]: 147 396 documents overall; Kaupunginhallitus 8 813, Kaupunginvaltuusto 3 612, plus Swedish-language duplicates such as Stadsfullmäktige 3 478.
- The README warns the sources are undocumented and can change. The old OpenAhjo API [carries a 12/2023 not-in-production note](https://avoindata.fi/data/en/dataset/4d992f0d-47a5-4645-aaaa-e5f1316bfe40/resource/be779e11-d0fe-4345-9263-c92af8214d42).

### Inferences
- Order: parser fix, full text, timeline, MCP. Launching MCP before full text would test the weakest version and could falsely show no demand.
- Full text brings new duties. The text names people (a sampled decision records a named architect heard at a meeting). Check GDPR handling before redistributing, even for public records, despite [section 9 of the Copyright Act](https://www.finlex.fi/fi/laki/ajantasa/1961/19610404) on decisions. Not legal advice.
- Relying on an undocumented proxy is an acceptable risk for a prototype but not a paid service. Ask the city about a supported route.

### Gaps
- Not assessed: `kartta.hel.fi/suunnitelmat`'s machine-readable access, the source for member data, and appeal data in the decision system. The first could change the priority of several rows.
- Effort sizes are my estimates with no team or code spike behind them.

## Questions the current data would answer wrongly or misleadingly

### Takeaway
The dangerous failures are confident negatives and status claims: "nothing is planned near you", "this plan is only a proposal", "the committee approved it". Any MCP tool should be built so these cannot be stated without qualification.

### Cited Findings: all [measured], as detailed above

| Question | What goes wrong | Evidence |
|---|---|---|
| "Is anything planned within 300 m of my address?" | Point-to-polygon error yields false negatives and false positives. Only proposals and committee plans are included, not permits or deviations | 33 % of matched zoning pins over 250 m from their plan; 81 % outside the polygon |
| "Is there nothing on my street?" | Absence is meaningless: unlocated items, classifier misses, no official-holder decisions, coverage begins 2013 | 105 unlocated; 338 traffic-chief plan subjects uncovered |
| "Has this zoning plan been approved?" | `proposal` stays forever, even after Council action | 256 of 298 zoning cases appear at City Board or Council |
| "What is the current status?" | A record may be an earlier decision, because one with a drawing outranks a later one | `better_decision`; 70 of 905 have later decisions |
| "How many plans were approved in 2015?" | Title wording counted as outcome | 220 title-only approvals; 173 `other`, 166 of them 2013–2017 |
| "Which plans were tabled or returned?" | Undercount | 12 labelled vs 31 found in text |
| "Why was it decided?" "What does it cost?" "How many homes?" | Excerpts hold none of this; an assistant may guess or generalise from the drawing title | Floor area and cost in 0 of 905 stored records |
| "Which plans concern cycling, trees or noise?" | Near-total miss, and it looks like a complete list | 7 vs 498; 14 vs 520; 1 vs 242 |
| "Who voted how? Was there dissent?" | No data; "no dissent found" would be false reassurance | 0 stored; 76 and 4 in text |
| "Summarise this decision" | For 357 records the summary is an appeal notice, and the assistant may read "no appeal allowed" as the decision's substance | Boilerplate in 36 % of summaries |
| "Can I still appeal or object?" | Truncated or generic notice, no deadlines for plans. This has legal consequences; send the user to the document | No display periods; only Kerro kantasi `close_date` |
| "Which district has the most plans?" | Counts are confounded by geocoding to district centres and street names, and by 2017 source changes | 438 at district level |
| "Was there a consultation before this decision?" | Consultations and decisions are not linked | `kk-` slugs, no case id |
| "Which plans were decided this week?" | Publication lags; drawings attach later (README and `scrape_decisions`) | Newest decision 27 Oct 2026, data of 1 Nov; a gap may also mean no plan decisions since |
| "What does the plan drawing show?" | The linked file is a guess and may be a location map or a report | README warning; drawing accuracy unreviewed |

### Inferences
- Tool design rules that follow:
  - Return `coverage` and `basis` fields with every answer.
  - Label stage as "as of this committee decision", never as current status.
  - Report location precision, and refuse radius answers at street or district precision, or answer "in the same district; check the drawing".
  - For legal questions, give the link and the city's contact point rather than an answer.
- These questions make a practical evaluation set. Running them before launch against a hand-checked answer key would measure the real error rate that this research only estimates.

### Gaps
- The error rate of real assistants using such data was not tested. The above predicts failures from the data alone.
- My stage cross-check uses keyword patterns, so its counts are indicative. A hand-labelled sample is needed.
