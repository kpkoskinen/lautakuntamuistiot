# Asking questions of Helsinki's decisions: prior art, data, feasibility, next steps

*Research report, 2026-11-02. Scope: a service (most likely an MCP server used from Claude
or another assistant) that answers questions about the **content** of Helsinki's meetings
and decisions, not only plan locations. Typical questions:*

- *"What is going on in area X?"*
- *"What has been decided on project Y?"*
- *"Can I get all the material and drawings concerning road Z?"*

*Builds on this repository's datasets. Protocol choices: read-only, MCP spec
2026-07-28, local first.*

*Companion to [MCP service for municipal decisions](MCP%20service%20for%20municipal%20decisions.md),
which covers comparable services and their uptake, MCP engineering and hosting cost, and
legal constraints in more depth. This report adds the inventory of Helsinki's sources
(§2), feasibility by question type (§3) and an experiment plan built on the full decision
text (§5). Where the two disagree on numbers, the cause is the date: this report was
measured after the summary parser fix of 2 Nov 2026, which replaced 365 appeal-notice
summaries.*

**Verification key.**
- **[LV]** = live-verified against the endpoint on 2026-11-02.
- **[repo]** = measured in this repository's `data/`.
- **[code]** = read from City-of-Helsinki source code on GitHub.
- **[web]** = taken from a web page.
- **[S]** = seen only in search snippets.
- **[I]** = our inference.

---

## 0. Answers in brief

1. **Has anyone built this?** **No.**
   - Nobody has put meeting content, geography and documents/drawings together behind
     an MCP server or a comparable assistant integration, in Finland or anywhere else.
   - Pieces exist, almost all from 2026:
     - MCP servers over council systems: Dutch Notubiz, German OParl/SD.NET, NYC Legistar,
       UK ModernGov.
     - Geo-enabled planning MCPs: PlanNexus (UK), Regrid (US parcels).
     - One non-MCP project that geolocates minutes to parcels: `fbrocca/boza`.
     - AI digitisation of plan PDFs: UK MHCLG *Extract*, Norway's *Planslurpen*.
   - Nothing exists for Ahjo or paatokset.hel.fi, and Helsinki has no MCP of its own
     (§1).
2. **Is it feasible with our data?** **Not with our current datasets. Yes with what Helsinki
   already publishes.**
   - We store about 4 % of each decision's text, and the history of each case stops at
     the committee.
   - The search proxy we already query returns the **full decision text and the whole
     case history across bodies** (committee → City Board → Council, in Finnish and
     Swedish) [LV].
   - Helsinki also publishes:
     - council debates and votes (Datapumppu);
     - hearings with polygons (Kerro kantasi);
     - plans in preparation, street works and events (WFS);
     - a city project list.

   With these, all three question types can be answered from 2017 onward, with
   citations (§2, §3).
3. **The most pressing data problems:**
   1. Missing text.
   2. Missing case history, which makes the "current stage" wrong.
   3. Points instead of extents for geography.
   4. Attachment lists missing from 2017 on, and half of the drawings have no text
      layer.
   5. No project / alias layer ("Kruunusillat" is never named in the decisions).
   6. Personal data, and following the city's removals.
   7. A single undocumented source.

   Actions for each are in §4.
4. **Next steps.** A three- to four-week experiment (§5):
   1. A gold set of 40 real questions.
   2. Harvest the full-text corpus for plan-related cases.
   3. Build a street/area gazetteer from the city's own registers.
   4. Write a local MCP server with five tools.
   5. Measure retrieval recall and citation accuracy with Claude.
   6. In parallel, write to the city about the proxy, Ahjo API access and personal-data
      removal.

---

## 1. Prior art: has anyone done this?

### 1.1 Closest implementations

| Project | What it is | Geo? | Documents | Status | Lesson for us |
|---|---|---|---|---|---|
| [Baarn Raadsinformatie MCP](https://glama.ai/mcp/servers/tiemenrtuinstra/baarn-raadsinformatie) (NL) | MCP over one municipality's Notubiz: meetings, agenda items, documents, semantic search | no | Downloads PDFs, runs OCR, embeds them, syncs every 6 h | repo, inactive [LV] | Pre-extracting and syncing beats live fetching at question time |
| [ratsinfo-mcp](https://github.com/MarcProe/ratsinfo-mcp) (DE) | MCP over any SD.NET RIM / OParl: full-text search including PDFs, `pdf_as_markdown` with page and term filters and a character cap | no | PDF to Markdown, 20 MB cap, only from the instance's own host | repo, 186 tests [LV] | **A PDF tool with limits** keeps whole attachments out of the model's context |
| [Nordstemmen KI-Connector](https://nordstemmen-mcp.levinkeller.de/) (DE) | **Live** remote MCP over one town's OParl, 2007→ | text only | Embeddings in Qdrant | live [LV] | Semantic search plus **exact lookup by document number** |
| [BetaNYC nyc-council-mcp](https://github.com/BetaNYC/nyc-council-mcp) (US) | Civic NGO's MCP over NYC Legistar: bills, hearings, votes, bill history | **no** | no PDF tools | released May 2026 [LV] | A fast local index next to live API tools for freshness; ambiguous ids and stale indexes are its documented pitfalls |
| [AI Open Overheid Toolkit](https://github.com/maikell/ai-openoverheid) (NL) | Amsterdam council (Notubiz), Woo documents, **BAG address lookup** | address tool beside the council tools, not joined to them | Woo by UUID | repo [LV] | Shows the tools side by side, never joined |
| [PlanNexus MCP](https://pypi.org/project/plannexus-mcp/) (UK) | ~363 planning authorities: search by text, postcode, **lat/lng + radius**; constraints at a point | **yes** | not mentioned | commercial preview [LV] | Shape for the spatial tool: point + radius, area id |
| [Regrid MCP](https://support.regrid.com/docs/mcp-server) (US) | Parcels and zoning, point/polygon/bbox | **yes** | none | production [LV] | Same |
| [Planslurpen MCP](https://glama.ai/mcp/servers/@2re1million/planslurpen_mcp) (NO) | AI-interpreted zoning plans, looked up by cadastral id | cadastral id | AI-extracted provisions, with a quality warning | beta [LV] | Reading plans with AI works, but needs a confidence flag |
| [fbrocca/boza](https://github.com/fbrocca/boza/pull/1) (US, not MCP) | Planning and council minutes **linked to parcels**, a timeline per case | **yes** | ~2 GB of PDFs reduced to text, deep links to the page | static site, Oct 2026 [LV] | Matching chain: case number → parcel → address → street → place. The best worked example of geolocating meeting items. |
| [Kotihiiri](https://kotihiiri.eu/) (FI, not AI) | Meetings, items and votes of 55 Finnish municipalities in one place, with a map section | map unclear | links only | live [LV] | Finnish demand exists; many municipalities show as "waiting for permission" |
| [MHCLG Extract](https://mhclgdigital.blog.gov.uk/2026/06/17/extract-is-here-ai-powered-planning-data-for-every-council-in-england/) (UK) | Scanned planning PDFs → spatial data with Gemini, in use by ~50 councils | yes | yes | live; every output reviewed by an officer [LV] | About ⅔ of outputs needed only minor edits. Drawings can be machine-read, but not without review. |

Other relevant items:
- **Finnish MCP servers** cover national legislation only: Finlex, and the Eduskunta
  (parliament) API via `JaakkoSan/finlex` [LV]. There is also a third-party avoindata.fi
  CKAN gateway [S].
- **City MCP launches:** Seoul (real-time city data, July 2026) [LV] and data.gouv.fr
  (experimental national MCP) [S]. Neither carries decision content.
- **Helsinki** has nothing like this. Its AI register lists 14 systems, none of them for
  decisions [LV]. The city has:
  - a general RAG kit, [hel-rag-service](https://github.com/City-of-Helsinki/hel-rag-service);
  - a **disabled** `decision_embeddings` index (OpenAI text-embedding-3-large) in the
    paatokset Drupal configuration [code].

  The city could add semantic search to paatokset.hel.fi later, so our design should not
  depend on being the only one.

### 1.2 What the research says

- **Summaries of council meetings contain factual errors**, whatever the model size, and
  LLMs judge factual consistency poorly: MeetingBank, ACL 2023 [S]; TofuEval,
  [arXiv 2402.13249](https://arxiv.org/abs/2402.13249) [LV abstract].
- **RAG over planning documents helps less than expected.**
  - One 2026 study found RAG had little or negative effect on plan evaluation, while
    multi-agent setups helped [S].
  - Another found RAG improved automatic scores but not expert ratings, and blamed
    text-only retrieval [S].
  - A Tel Aviv plans repo reports faithfulness of 0.66 [S].
- **CitiLink** (ECIR 2026) extracted metadata and votes from Portuguese municipal minutes
  with an LLM, then searched them with BM25 and facets
  ([arXiv 2601.18374](https://arxiv.org/abs/2601.18374)) [LV].
- **There is no question-answering benchmark over council minutes.** We have to build our
  own gold set (§5).

**Design consequences:**
- Answers must be built from **retrieved, cited sections and structured case data**, not
  from free-form summaries.
- The "current status" of a case should come from a table, never from the model.
- Drawings should be **linked** with their metadata, not interpreted.

---

## 2. What Helsinki actually offers

### 2.1 Sources compared with what we use

| Source | We use today | What else it offers | Access | Verified |
|---|---|---|---|---|
| **paatokset ES proxy** `paatokset-elastic-proxy.api.hel.ninja/paatokset_decisions/_search` | subject, url, date, case id of committee decisions | **`decision_content`** (Päätös, Käsittely) and **`decision_motion`** (Päätösehdotus, *Esittelijän perustelut*), full HTML text, median 7.6k characters per decision. **All bodies:** City Board, Council (fi + sv), office holders. Also `category_name` (e.g. *Asemakaavoitus*), `sector_id`, `field_decision_section` (§), `has_translation`. ~147k decisions, effectively **2017→** (27 stray from 2015–16). `match_phrase` on drawing number "32179/1" or "nro 12863" finds the case chain. | open, undocumented; only `_search`/`_msearch`; paging past 10k needs `search_after` | LV |
| same proxy, `paatokset_meetings` | — | 7,146 meetings 2011→: id (e.g. `U540202632`), body, date, whether the agenda and minutes are published, documents page | open | LV |
| same proxy, `paatokset_policymakers` | — | 3,945 bodies and office holders, organisation hierarchy, sector | open | LV |
| same proxy, `paatokset_allu` | — | Street and area-use **permit decisions** since 2026-08-20 (excavation, area rental, events, temporary traffic arrangements), with address text and PDF | open | LV |
| Decision page `paatokset.hel.fi/fi/asia/{hel-id}` | heading, summary, one drawing | **Full attachment list (Liitteet)**; *Päätöshistoria*; presenter, preparer and contact names (not in ES) | open HTML | LV |
| Meeting documents page, `ahjojulkaisu.hel.fi/{GUID}.pdf` | — | Whole agendas and minutes as PDF | open | LV |
| **Datapumppu** `hel-datapumppu.api.hel.fi` | — | **City Council only**, 2018→: agenda items with decision HTML and decision history, **speaking turns** (person, party, timestamped video link), **votes** including *ponsi* motions | open, undocumented | LV |
| Council discussion minutes (`…/kaupunginvaltuusto/keskustelupoytakirjat`) | — | Verbatim debate transcripts, PDF, council only | open | LV |
| Meetings calendar JSON `paatokset.hel.fi/fi/ahjo_api/meetings` | — | All meetings: status, moved or cancelled | open | LV |
| **Kerro kantasi API** `kerrokantasi.api.hel.fi/v1/` | hearing title, abstract, centroid, images | `?include=geojson` gives **hearing polygons** (258/402). Also section texts and files, `borough`, labels, contact persons, 39 **projects with phases**, and 108k comments (CC BY-NC-SA, with comment geometry). | open | LV |
| **kartta.hel.fi WFS** `avoindata` (300 layers) | `Kaavahakemisto_alue_kaava_voimassa` | See §2.2: **plans in preparation**, street register with geometry, addresses, place names, properties, blocks, plan units, buildings, district divisions, excavation works, events, temporary traffic arrangements, building bans | open, CC BY 4.0 | LV |
| ptp.hel.fi | zoning drawings and reports | Street and park plan PDFs (`pw_docs`), shown in the closed map app `kartta.hel.fi/suunnitelmat` | open PDF, no open index | LV |
| **City projects** `liikenne-elastic-proxy.api.hel.ninja/projects/_search` | — | 226 hel.fi "Suunnitelmat ja rakennushankkeet" projects: district, **phase** (12 values), theme, type, plan and construction schedules, external site. Same proxy: `districts`, `street_data`, temporary parking signs with geometry. | open, undocumented | LV |
| Servicemap v2 `api.hel.fi/servicemap/v2/` | — | 237 sub-district boundaries with `ocd_id`, address geocoding, fi/sv street names | open | LV |
| Linked Events `api.hel.fi/linkedevents/v1/` | — | Residents' evenings and information sessions on plans (`text=asemakaava` → 414 events) | open | LV |
| HRI CKAN | — | Catalogue: 93 city-environment datasets, CC BY 4.0 (address list, place names, properties, blocks, plan units, building bans, public-area register, Allu, 3D) | open | LV |
| hel.fi/static/public/hela | 2013–2017 bulletins | Decision text on the same pages (to be extracted) | open | used |

**Closed or dead:**
- **OpenAhjo** (`dev.hel.fi/paatokset/v1`) is dead: "not in production" since late 2023,
  and the connection times out [LV].
- **The official Ahjo REST API** is mirrored at `paatokset.hel.fi/ahjo-proxy/…` but needs
  an `api_user` role (403) [LV, code].
- **The Allu external API** needs a login [code].
- **Helsinki Kanava video API** needs an organisation secret [code].

### 2.2 WFS layers that answer "what's happening in area X"

All of these are open, CC BY 4.0, updated daily, and include geometry [LV].

| Layer (`avoindata:`) | Features | Use |
|---|---|---|
| `Kaavahakemisto_alue_kaava_vireilla` | 80 | **Zoning plans in preparation**, by plan number. The layer has **no name or description**, so it must be joined to decision text by plan number. |
| `Kaavahakemisto_alue_kaava_voimassa` (already used), `…_kumottu`, underground variants | 4,413+ | Plans in force and repealed: extents and drawings |
| `Osayleiskaavahakemisto_alue`, `Rakennuskieltoalue_*` | 10 / 7 | Master-plan parts, building bans with decision dates |
| `YLRE_Katualue_alue` (+ `YLRE_Katuosat_*`, `YLRE_Viheralue_alue`) | 7,769 streets | **Street-area polygons by street name**, with district, sub-district and major district. This is the gazetteer and geometry for "road Z". |
| `Helsinki_osoiteluettelo`, `Helsinki_nimisto` | 58k / 7.6k | Addresses and place names in fi/sv: the rest of the gazetteer |
| `Maavesi_osa_alueet`, `…_kaupunginosat`, `Piirijako_*` | 148 sub-districts | The polygons that define "area X" |
| `Kiinteisto_alue`, `Helsingin_korttelit`, `Kaavayksikot`, `Rakennukset_alue_rekisteritiedot` | 36k / 6k / 40k / 85k | Properties, blocks, plan units (carry the plan number), buildings. These join the land-sale and lease decisions that cite property or block ids. |
| `Kaivuilmoitus_alue/_piste` | 3,546 | Current and upcoming **excavation works**, with purpose and address |
| `Tilapainen_liikennejarjestely_*`, `Tapahtumat_*`, `Aluevuokraus_*` | 272 / 100 / 1,865 | Temporary traffic arrangements, events, area rentals |

### 2.3 What Helsinki does *not* offer

1. **No documented, open decision API.** The ES proxy is the de facto API. It is
   undocumented, and its old standalone repo is archived.
2. **No full text before 2017** in ES. 2013–2016 is in the hela static pages. Before 2013
   nothing can be retrieved programmatically (the README's hard floor).
3. **No geometry on decisions**, only text: street names, plan numbers, block and
   property ids.
4. **Attachments and drawings exist only as PDFs.** They are not indexed, about half have
   no text layer, and the attachment list appears only on the decision page. Some
   attachments are not public.
5. **No open layer or index of street and park plans.** Plans in preparation have no
   names. City projects have a district but no geometry.
6. **No committee debate records and no video transcripts.** Debate exists only for the
   Council, through Datapumppu and the discussion-minutes PDFs.
7. **No open building-permit feed**, and **no open Allu API** (only the WFS snapshots, and
   Allu decision PDFs since 2026-08).
8. **No MCP server or AI search over decisions.**

### 2.4 Keys that link the sources

| Key | Example | Where |
|---|---|---|
| **Case id** `HEL-YYYY-NNNNNN` | HEL-2022-003213 | ES `unique_issue_id`, decision URL, Datapumppu `caseIDLabel`. Kerro kantasi only in body text. **Missing for our 809 hela records** (synthetic `hela-<uuid>` ids). |
| **Plan number** (kaavatunnus) | 12863 | WFS in force, in preparation and plan units; decision text "(nro 12863)" |
| **Street-plan drawing number** | 32179/1 | Only in decision text and PDFs (497 of our records mention one) |
| Park plan number | VIO 6037 | Decision text |
| Meeting id, policymaker id | U540202632, U540 / 00400 / 02900 | ES meetings, Datapumppu |
| Allu application id | KP…, TP…, LJ…, AL… | WFS `hakemustunnus`, ES allu |
| Property, block, building ids | 91-43-9903-4, 0910410062, `vtj_prt` | WFS; land-sale and lease decisions |
| **Street name** (fi/sv) | Mannerheimintie / Mannerheimvägen | YLRE, address list, Servicemap. The key for matching mentions in text. |
| Area names and codes | sub-district 493, "20 LÄNSISATAMA" | WFS, Servicemap `ocd_id`, Kerro kantasi `borough`/labels, project `district` |

---

## 3. Feasibility by question type

### Corpus size

The corpus is small enough to index on a laptop.

- **All decisions:** ~147k decisions since 2017 × ~7.6k characters median ≈ **1 GB of text**.
- **Plan-related cases only:** the cases where the committee decided, plus the chain of
  each case through all bodies. Our 940 committee cases alone have ~2,500 decision
  documents across bodies.

### "What has been decided on project Y?"

- **Today:** a keyword search over titles. The *stage* is wrong for most zoning plans,
  because we store only the committee proposal. In 56 % of our cases the City Board or
  Council made later decisions that we do not hold [LV].
- **With the full ES case chain:** feasible. The answer is a timeline per case (body, date,
  §, decision, link), plus *Esittelijän perustelut* sections retrieved for the "why".
  For Council items, Datapumppu adds votes and debate.
- **The real gap is the project → cases mapping.** City brand names rarely appear in the
  decisions. For "Kruunusillat" our data has 1 title hit, while the decisions say
  *Kruunuvuorenrannan joukkoliikenneyhteys* and *Kruunuvuorensilta* (43 records)
  [repo]. Raide-Jokeri gives 15 hits spread over many street names.
- **What it takes:** an alias and project table (§4, P5). The city projects index (226
  projects) and Kerro kantasi projects (39) can seed it.

### "What is going on in area X?"

- **Today:** pins near X. 25 % of pins are district centroids; a "street" pin is one point
  on a street that may be kilometres long.
- **With Helsinki's data:** feasible, as an **aggregation by sub-district polygon** over
  six sources:
  1. decisions geotagged from their full text (streets, plan numbers, blocks);
  2. zoning plans in preparation and in force (polygons);
  3. Kerro kantasi hearings (polygons);
  4. city projects (district);
  5. excavation works, events and temporary traffic arrangements (WFS geometry);
  6. Linked Events information sessions.
- **This is the most valuable question type.** Today nobody can answer it from one place,
  and every source it needs is open.
- **Its quality depends on the gazetteer and on honest precision flags** ("on Hämeentie"
  is not the same as "in Kallio").

### "All material and drawings concerning road Z"

- **Feasible for 2017+, with known limits:**
  1. Street name, inflected forms included, matched against the full text.
  2. Plus the YLRE street polygon intersected with plan extents and hearing polygons.
  3. For each matched case, the attachment list from its decision page.
  4. Plus the drawing numbers found in the text.
  5. Plus links to zoning drawings and reports from ptp.hel.fi.
- **Limits:**
  - Completeness cannot be promised: no material before 2013, non-public attachments,
    street plans without an open index.
  - Drawings are **found and linked, not read**. About half are image-only scans or
    outlined text, and text extracted from vector sheets comes out in fragments
    ("Ko r ppaa tie"). Reading only the title block (drawing number, title, date,
    revision) with OCR or a vision model is realistic; interpreting the whole sheet is
    not (cf. MHCLG Extract's officer review).

### Verdict

- **Feasible.** The hard part is data engineering, not the MCP server. The MCP layer is a
  few hundred lines.
- **Everything rests on one undocumented endpoint.** That is a project risk to raise
  with the city early, not a technical one to engineer around.

---

## 4. The most pressing data problems and what to do

Ranked by severity, with effort in brackets. Measurements are from `data/` on 2026-11-02
[repo] and from small probes [LV].

**P1. Almost no content (critical; low effort).**
- **Problem:**
  - 809 / 1,832 records (44 %, all 2013–17) have no summary.
  - 70 % of the paatokset summaries are cut at 320 characters, about 4 % of the text.
- **Action:**
  1. Store `decision_content` and `decision_motion` (raw HTML plus clean text) for
     every document of every case, and the Swedish version where `has_translation`
     is set.
  2. Extract the text from the hela pages for 2013–16.
  3. **Chunk on the document's own section headings** (*Päätös, Esitys, Esittelijän
     perustelut, Kaavaratkaisun keskeinen sisältö, Vuorovaikutus…*), not on fixed
     windows. Each section then becomes a citable unit with body, date and §.

**P2. Case history stops at the committee, so the "stage" is wrong (critical; low–medium).**
- **Action:**
  1. Model **Case 1–n Decision 1–n Section / Attachment**.
  2. Fetch the whole chain per `unique_issue_id`.
  3. Derive `current_stage` and `as_of` from the latest decision.
  4. For zoning, cross-check against the WFS acceptance and validity dates.
  5. Detect appeals and legal validity from the text (*valitus, hallinto-oikeus, KHO,
     lainvoimainen*).
  6. Recover the real HEL case ids of the 809 hela records from their text, so they can
     join.

**P3. Geography is points, not extents (high; medium).**
- **Action:**
  1. Join zoning decisions to WFS polygons by plan number: 752 / 816 zoning records
     already name one. Use both the in-force and in-preparation layers.
  2. Keep the Kerro kantasi polygons (today we keep only centroids).
  3. Build a **gazetteer from the city's own registers** (YLRE streets, address list,
     place names, sub-districts) instead of public Nominatim. It is official, fi/sv, has
     polygons, carries no ODbL share-alike, and has no rate limit.
  4. Geotag the **full text**, not just the title, with the existing inflection logic in
     `locate.py` and an exact match against that closed list.
  5. Precompute each item's sub-district membership and keep a precision flag (extent /
     street / district) that answers must surface.

**P4. Attachments missing for 2017+; half of the drawings unreadable (high; medium–high).**
- **Problem:** none of the 1,023 paatokset records has an attachment list. Of 12 sampled
  drawings, 4 had no text layer and 2 had fewer than 20 words.
- **Action:**
  1. Harvest the attachment list (name, number, URL) from every decision page.
  2. Fingerprint each PDF by SHA-256.
  3. Classify the attachment type with the existing `best_drawing` vocabulary.
  4. Extract text with `pdftotext` first. Where a page has fewer than ~50 words, use
     OCR or a vision model **on the title block only**.
  5. Make the drawing number (NNNNN/N, VIO NNNN) a first-class key.

**P5. No project or alias layer (high; medium).**
- **Action:** a curated `project` table:
  - canonical name and fi/sv aliases (*Kruunusillat / Kronbroarna*);
  - cases, plan numbers, drawing numbers, streets, polygon.
- Seed it from the city projects index and Kerro kantasi projects. Propose further links
  with an LLM over the full text, and have a person approve them.
- Typed links (same case, same plan number, same drawing series, cites a decision, same
  street within a time window) in plain relational tables are enough at this scale.
  Full GraphRAG is not needed.

**P6. Personal data, and following the city's removals (high legally; medium).**
- **Problem:**
  - 16 % of the sampled full-text documents contain contact data (officials' names,
    phone numbers, `@hel.fi`).
  - The index also holds individual-case bodies, e.g. the *Sosiaali-, terveys- ja
    pelastuslautakunnan yksilöasioiden jaosto*, with 3k decisions.
  - Finnish practice is to remove personal data from minutes published online after the
    appeal period. A mirror that keeps what the city has removed becomes a controller
    in its own right.
- **Action:**
  1. **Allow-list bodies and categories:** city-environment committee, City Board,
     Council, plan-related office-holder decisions. Never individual-case divisions.
  2. Strip contact blocks and person names before indexing.
  3. Do not index Kerro kantasi comments (CC BY-NC-SA, may carry names).
  4. Re-check stored documents against the source, and delete what vanished or changed.
  5. Ask `tietosuoja@hel.fi` for the removal period. **We could not find Helsinki's
     exact rule.**
  6. Write a short DPIA-style note.

**P7. One undocumented source, no change signal (medium; low).**
- **Problem:** the proxy is undocumented, and no modification timestamp was seen in a
  sample document.
- **Action:**
  1. Store `fetched_at`, the raw payload and a content hash per document.
  2. Keep the daily delta for new items, and add a rolling re-hash (last 90 days daily,
     older items monthly) to catch corrections and removals.
  3. Put "source, decision date, retrieved on" in every tool result.
  4. Keep the pipeline source-agnostic, so an Ahjo REST API export can replace the
     proxy.
  5. **Ask the city for permission and for `api_user` access** to the Ahjo proxy.

**P8. Finnish search quality (medium; low).**
- **Evidence:** on Finnish MIRACL, plain BM25 scores 45.8 nDCG@10 and BGE-M3 / mE5-large
  ~78–80 ([BGE-M3 paper](https://arxiv.org/abs/2402.03216)). That is Wikipedia text; no
  Finnish administrative benchmark exists.
- **Action:**
  - **Hybrid search:** BM25 over lemmatised and compound-split tokens (Voikko/Raudikko)
    plus dense embeddings (BGE-M3 or mE5).
  - Exact fields for case, plan, drawing and property ids and street names.
  - Tune only against our own gold set.

**P9. Unmeasured quality (medium; low).** `quality_sample.csv` is still unreviewed, so
plan type, drawing and location accuracy are unknown. **Action:** review it (half a day),
and build the gold question set in §5.

**P10. Licences and AI transparency (medium; low).**

| Material | Terms | Handling |
|---|---|---|
| Decisions | No copyright (Copyright Act § 9) | Can be indexed and quoted |
| Consultant drawings and reports | Probably protected | Link only, short snippets |
| HRI / WFS data | CC BY 4.0 | Credit "Helsingin kaupunki, kaupunkimittauspalvelut" |
| Kerro kantasi | Data ODbL, comments CC BY-NC-SA | Comments not indexed (P6) |

- **EU AI Act Art. 50** (applies from 2 Aug 2026): tell users they are dealing with AI
  [web, secondary sources].
- **Every tool response should carry:** "unofficial, not the City of Helsinki", the
  source links, and the as-of date.

---

## 5. Next steps: an experiment in four weeks

The goal is to learn whether the answers are good and complete enough, before building
anything public. Everything runs locally and read-only.

**Step 0. Write to the city (day 1, runs in parallel).** Contact the paatokset team /
`hri@hel.fi` and `tietosuoja@hel.fi`:
- Is heavier, identified use of the ES proxy acceptable?
- Can we get `api_user` access to the Ahjo REST proxy, or a bulk export?
- How long does personal data stay published?
- Is the city planning semantic search over decisions (the disabled `decision_embeddings`)?

**Step 1. Gold set (week 1, ~1 day).**
- 40 real questions:
  - 15 "area X" (e.g. Malmi, Jätkäsaari, Kalasatama);
  - 15 "project Y" (Kruunusillat, Raide-Jokeri, Hernesaari, Vuosaari plan 12863, …);
  - 10 "road Z" (Mannerheimintie, Hämeentie, Neptunuksenkatu, …).
- For each question, list the cases, documents and drawings a correct answer must cite,
  checked by hand on paatokset.hel.fi.
- Review `quality_sample.csv` at the same time.

**Step 2. Corpus spike (week 1–2).** A new `harvest_cases` step:
- For every case id in `plans_dataset.json`, plus all City Board and Council decisions in
  the *Asemakaavoitus* / street / traffic categories, fetch the whole case chain from ES.
- Store the full text, split into sections, plus the attachment list from the decision
  page.
- Write to **SQLite** (FTS5 with simple Finnish stemming, then `sqlite-vec` with BGE-M3)
  or Postgres/PostGIS. Raw payloads are kept.
- Allow-list of bodies as in P6.
- **Measure:** documents, cases per stage, time per 1,000 cases.

**Step 3. Gazetteer and geotagging (week 2).**
- Load YLRE streets, the address list, place names, sub-districts and zoning plans (in
  force and in preparation) from the WFS.
- Geotag every section by matching street, place and plan-number mentions.
- Join the Kerro kantasi polygons.
- **Measure** against the gold set: does each "area X" question's expected case get the
  right sub-district?

**Step 4. Minimal MCP server (week 3).** A Python package, separate from the stdlib-only
scrapers, stdio transport, read-only. Five tools:

| Tool | Inputs | Returns |
|---|---|---|
| `search_decisions` | text, optional sub-district / street / plan number / drawing number / body / date range | ranked sections with case id, body, date, §, link, precision flag |
| `get_case` | HEL case id | timeline across bodies, `current_stage`, `as_of`, attachments, related cases |
| `whats_happening` | sub-district name, or a point + radius | grouped: decisions, plans in preparation, hearings (open first), projects, current works and events |
| `find_material` | street name or project | all cases, attachments and drawings, with links and drawing numbers |
| `get_section` | document id + section | the full text of one section (capped), for quoting |

- Every result carries its sources, an as-of date and the "unofficial" notice.
- No tool returns generated summaries.
- Drawings are links plus metadata.

**Step 5. Evaluation (week 4).**
- Run the 40 questions through Claude with the server.
- **Score:**
  1. retrieval recall of the expected cases and documents;
  2. citation correctness (every claim traceable to a returned section);
  3. stage correctness;
  4. completeness on the road-Z questions.
- Compare with a baseline of the same assistant using web search on paatokset.hel.fi.
- **Decide go/no-go on a shared deployment** and on whether drawing title-block OCR (P4)
  pays off.

**Not in the experiment:**
- Datapumppu council debates and votes (add after step 5 if "project Y" answers need them).
- Swedish-language answers.
- Material before 2017 beyond what hela already gives.
- A web chat UI: the MCP client (Claude or another assistant) is the UI.

---

## 6. Open points

- **Helsinki's exact rule for removing personal data** from paatokset.hel.fi, and whether
  the ES proxy reflects removals immediately.
- **No modification field in the ES documents:** seen in one sample only; the mapping is
  not readable through the proxy.
- **Whether hela pages carry the real HEL case id.**
- **How appeals appear in the index.**
- **Licence of the proxy content:** OpenAhjo used CC BY 4.0, but the proxy states none.
