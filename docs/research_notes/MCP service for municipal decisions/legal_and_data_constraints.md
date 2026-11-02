# Legal, licensing, data-source and data-quality constraints on an MCP service for Helsinki decisions

Research notes as of 2026-11-02, not legal advice. Labels: **[Rule]** means clear statutory or licence text that I read. **[Interp.]** means interpretation, mine or a commentator's. **[Confirm]** means a lawyer or the City's data protection officer should confirm. Web content was treated as data. The repository was read only.

**Corrections to the brief, checked against sources:**
- Kuntalaki 108 § covers municipal *notices*, not decisions. The removal rule for minutes is **140 §**, and 142 § covers administrative-court decisions.
- 13 b § of the Copyright Act is confirmed. I could **not confirm a 13 c §**: Act 263/2023 lists 13 b as new but not 13 c.
- The Produced Work versus Derivative Database choice is not binary for geocoding. The OSMF guideline uses a separate "substantial extract" test.

## Synthesis: what changes from a static map to an LLM-accessible service, plus do's, don'ts and risks

### Takeaway
The current product is low risk because it holds short excerpts, links out to originals, and shows caveats next to each pin. An MCP service with full text removes all three protections:
- It would become a searchable personal-data copy that outlives the City's removal.
- It would serve possibly protected attachment text.
- It would strip caveats as an LLM restates the content as fact.

Recommended first scope: metadata and decision-text excerpts only, no attachment or PDF text, names removed, deterministic tools only, and appeal questions answered only by linking to the original.

### Cited Findings

**What changes**

| Dimension | Static map today | MCP with full text and PDFs | Why it matters |
|---|---|---|---|
| Personal data | Short excerpts. My crude role-plus-name check found 0/1 727 summaries (see Data quality) | Decision pages name contact officials with phone and email; attachments are titled e.g. "Muistutukset" | GDPR applies to us as controller |
| Findability | Browse by pin | Query by a person's name, across years | The City's duty is to take names offline after the appeal period ([Kuntalaki 140 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@)) |
| Copyright | "Linked, not copied" ([README](../../../README.md)) | Copies and restates attachments | 9 § 2 mom. carve-out applies ([TN 2020:4](https://www.edilex.fi/tekijanoikeusneuvosto/fi/20200004.pdf)) |
| Caveats | Experimental notice and per-pin precision shown ([README](../../../README.md)) | The model decides what to repeat | [Interp.] Disclaimers do not survive restatement |
| Licence notices | Map credit line | Needs a machine-readable notice in every result | ODbL 4.3 covers anyone "exposed to" a Produced Work ([ODbL](https://opendatacommons.org/licenses/odbl/1-0/)) |
| Geocoding | Batch, cached, ≤4/min | Temptation to geocode live on LLM queries | [Nominatim policy](https://operations.osmfoundation.org/policies/nominatim/) |
| Source load | Daily job | Unbounded agent loops; PDF fetches hit a host that disallows crawlers | [ahjojulkaisu robots.txt](https://ahjojulkaisu.hel.fi/robots.txt) |

**Do**
1. **Link to the original for every claim, and return `decision_url` in every tool result.** The README already treats hel.fi originals as authoritative. — [README](../../../README.md)
2. **Exclude personal names, phone numbers and emails from the index by default, including the "Lisätietojen antajat" block.** The City itself may publish only personal data necessary for access to information. — [Kuntalaki 140 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@)
3. **Re-check sources and propagate removal.** Today hearings already closed are not re-read and processed decisions sit in `seen_decisions`, so nothing detects a later redaction. — [README](../../../README.md); storage limitation in [GDPR Art. 5](https://gdpr-info.eu/art-5-gdpr/)
4. **Publish a privacy notice and an erasure and objection route before launch, and write a legitimate-interest assessment.** — [GDPR Art. 17](https://gdpr-info.eu/art-17-gdpr/), [Art. 6](https://gdpr-info.eu/art-6-gdpr/); [EDPB Opinion 28/2024](https://www.edpb.europa.eu/system/files/documents/2025-05/edpb_opinion_202428_ai-models_fi.pdf)
5. **Keep Kerro kantasi-derived data as a separate ODbL dataset and offer it for download.** — [ODbL 4.4–4.6](https://opendatacommons.org/licenses/odbl/1-0/); [Kerro kantasi terms](https://github.com/City-of-Helsinki/kerrokantasi-ui/blob/main/cities/helsinki/i18n/service-info/content.en.md)
6. **Serve coordinates from the cache or move to the City's CC BY address data.** — [Nominatim policy](https://operations.osmfoundation.org/policies/nominatim/); [HRI helsingin-osoiteluettelo](https://hri.fi/data/api/3/action/package_show?id=helsingin-osoiteluettelo)
7. **Ask the City before launch, and request a bulk copy under Julkisuuslaki 16 § 2 mom.** — [Act 621/1999, original text](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/1999/621/fin@)
8. **Complete the 100-record manual review first, and publish the results.** All four verdict columns are empty. — [quality_sample.csv](../../../data/quality_sample.csv)
9. **Return structured provenance and uncertainty fields, listed under Data quality.**

**Don't**
1. **Don't state, compute or infer an appeal deadline.** It depends on route, recipient and service date. — [Kuntalaki 134–138, 140 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@)
2. **Don't describe a plan as "valid" or "in force"; the dataset has no such field.** `approved` means only that the committee approved it. — [README](../../../README.md)
3. **Don't offer search by person name.** [Interp.] This is the feature closest to the mass dissemination rejected in *Satakunnan Markkinapörssi* and to the separate-controller logic of *Google Spain*. — [ECtHR GC commentary](https://inforrm.org/2017/07/06/case-law-strasbourg-satakunnan-markkinaporssi-oy-and-satamedia-oy-v-finland-no-journalism-exception-for-massive-exposure-of-personal-taxation-data-dirk-voorhoof/); [Hunton on C-131/12](https://huntonak.com/privacy-and-information-security-law/eu-court-justice-upholds-right-erasure-google-search-case)
4. **Don't bulk-crawl `ahjojulkaisu.hel.fi` for text extraction without the City's permission.** It serves `Disallow: /`, and a sampled PDF carried `x-robots-tag: noindex`. — [robots.txt](https://ahjojulkaisu.hel.fi/robots.txt)
5. **Don't return substantial verbatim text from consultants' reports, photos or drawings.** — [YM report 22/2018, pp. around 22](https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/161120/YMra_22_18_Rakennettua_ymparistoa_koskevan_tiedon_tekijanoikeus.pdf?sequence=1&isAllowed=y)
6. **Don't ingest Kerro kantasi comments.** They are CC BY-NC-SA and identified users' data is not to be disclosed to third parties. — [Kerro kantasi terms](https://github.com/City-of-Helsinki/kerrokantasi-ui/blob/main/cities/helsinki/i18n/service-info/content.en.md)
7. **Don't expose a generic geocoding tool, or call public Nominatim per query.** — [Nominatim policy](https://operations.osmfoundation.org/policies/nominatim/)
8. **Don't rely on the journalism exemption.** — [Data Protection Act 27 §](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2018/1050/fin@); [C-73/07 coverage](https://merlin.obs.coe.int/article/7340)
9. **Don't call the service official or imply City endorsement.** The README states independence. — [README](../../../README.md)
10. **Don't return spread pin positions as locations.** 48.1% of per-type GeoJSON pins are offset (see Data quality).

**Risk register**

| Risk | Likelihood / impact (my judgment) | Source |
|---|---|---|
| Undocumented Elasticsearch proxy changes or closes | Medium / high | README says sources "can change or vanish"; [helsinki-paatokset README](https://github.com/City-of-Helsinki/helsinki-paatokset) describes open endpoints as serving JS apps |
| Copy retains names after the City removes them | High if full text / medium to high | Kuntalaki 140 § |
| LLM states wrong appeal deadline, right is lost | Medium / high for the individual | Kuntalaki 135, 138 § |
| Regulator complaint from a named individual | Low to medium / medium | GDPR Art. 17, 21 |
| Share-alike dispute over combined data | Low / medium, if kept separate | ODbL 4.4–4.6; OSMF guidelines |
| Nominatim block | Low with cache / medium | Nominatim policy |
| AI Act penalties for auto-published summaries | Low if deterministic / medium | [Art. 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50) |

### Inferences
- [Interp.] The largest single decision is whether to include PDF contents. It simultaneously raises the personal-data, copyright, robots.txt and quality risks. Decision-page text carries much less copyright risk but still needs name removal.
- [Interp.] A tool-level `not_answerable` response for deadlines, validity and legal effect is a stronger mitigation than any disclaimer.

### Gaps
- No lawyer or DPO has reviewed any of this. Priority items for them are the GDPR legal basis, Art. 14 notice practice, and how 140 § affects re-publishers.

## Copyright: section 9 of the Copyright Act (404/1961), attachments, drawing PDFs, and text and data mining

### Takeaway
Decision text is free of copyright. Attachments are not automatically free, and consultant reports are the clearest risk. **[Rule]** Text and data mining (13 b §) permits making copies for analysis, not publishing the content, so it does not clear an LLM service that restates attachment text.

### Cited Findings
- **[Rule]** Under 9 § 1 mom. 4 kohta there is no copyright in decisions and statements of an authority or other public body. Under 9 § 2 mom. that does not apply to independent works contained in such documents. — [Tekijänoikeusneuvosto 2020:4, para 18](https://www.edilex.fi/tekijanoikeusneuvosto/fi/20200004.pdf)
- **[Rule]** Under 25 d § 4 mom., 9 § 2 mom. works may be reproduced in connection with the document, and used separately for the administrative or other purpose the document relates to. — [TN 2020:4](https://www.edilex.fi/tekijanoikeusneuvosto/fi/20200004.pdf)
- KKO 2000:56 holds that the purpose of 9 § is to protect the public interest attached to those documents. — [TN 2020:4, para 28](https://www.edilex.fi/tekijanoikeusneuvosto/fi/20200004.pdf)
- [Interp.] A Ministry of the Environment report argues that 9 § 2 mom. covers no fixed list of work types, and that authority memos, reports and studies are generally protected once they pass the threshold of originality, *especially documents received by an authority*. **Weight caveat:** the report is also the author's master's thesis, and the author alone is responsible for its conclusions. — [YM 22/2018](https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/161120/YMra_22_18_Rakennettua_ymparistoa_koskevan_tiedon_tekijanoikeus.pdf?sequence=1&isAllowed=y)
- [Interp.] The same report says a plan map is an authority document whether drawn in-house or by a consultant, and copyright problems with plan maps are unlikely. It adds that use for public debate and scrutiny is unrestricted, but that once use no longer serves the openness principle, the rightholder's consent is in principle needed if the threshold is met. — [YM 22/2018](https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/161120/YMra_22_18_Rakennettua_ymparistoa_koskevan_tiedon_tekijanoikeus.pdf?sequence=1&isAllowed=y)
- [Interp.] Building drawings are 9 § 2 mom. works if original, and the report says purely commercial use needs consent. — [YM 22/2018](https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/161120/YMra_22_18_Rakennettua_ymparistoa_koskevan_tiedon_tekijanoikeus.pdf?sequence=1&isAllowed=y)
- Standard consultant terms (KSE 2013, 6.2.1, as quoted in that report) bar the client from passing consultant material to third parties for other purposes without consent. — [YM 22/2018](https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/161120/YMra_22_18_Rakennettua_ymparistoa_koskevan_tiedon_tekijanoikeus.pdf?sequence=1&isAllowed=y)
- **[Rule]** 13 b § 1 mom.: a person with lawful access may make copies for text and data mining and keep them solely for that purpose, unless the author has expressly and appropriately reserved this right. 2 mom. gives research organisations and cultural-heritage institutions a non-reservable right for scientific research. — [Act 263/2023](https://finlex.fi/api/media/statute/9863/mainPdf/main.pdf). It implements Directive 2019/790, which the same act cites.
- 49 § protects catalogues and databases requiring substantial investment. [Interp.] The report states that the 9 § and 25 d § limits also apply to that protection through 49 § 4 mom. — [YM 22/2018](https://julkaisut.valtioneuvosto.fi/bitstream/handle/10024/161120/YMra_22_18_Rakennettua_ymparistoa_koskevan_tiedon_tekijanoikeus.pdf?sequence=1&isAllowed=y)
- Repository scale: 4 533 attachments are listed on 732 records. By name, 785 match "selostus", 376 "vuorovaikutus", 696 image words, and 148 match muistutus/mielipide/valitus/kirje/kannanotto. (Read-only check of [plans_dataset.json](../../../data/plans_dataset.json).)

### Inferences
- **Decision text, reasoning, plan numbers and dates:** free to reuse under 9 §. [Interp.] "Esittelijän perustelut" is reasonably an authority statement, but quoted third-party material inside it may not be.
- **Drawing PDFs and text extraction, different matter?** [Interp.] Yes in two ways. First, extraction makes a copy, so it needs 13 b § or another basis if the drawing is protected. Second, 13 b § covers the mining copy, not re-making the text available. Title-block text (plan number, scale, date) is unlikely to be original, but it may hold designers' names, so the problem shifts to personal data.
- **Consultants' reports, photos, third-party letters:** treat as protected. Do not return substantial text. Facts extracted from them are lower risk, and short quotation may be defensible, though I did not verify 22 §.
- **The TDM reservation:** [Interp.] Whether `robots.txt` counts as an "appropriate" reservation is unsettled and I found no Finnish authority. The City also may not be the rightholder for consultant material, so the reservation question could go either way. **[Confirm]**
- **Purpose of use:** [Interp.] The 25 d § 4 mom. "purpose the document relates to" wording fits public scrutiny better than a commercial product, so a paid service would carry more risk than a free civic one.

### Gaps
- The consolidated text of 404/1961 could not be retrieved from Finlex (API returned 404, page rendered client-side). 9 § is quoted via TN 2020:4, 13 b § via the amending act. 13 c § is unconfirmed, and I found no text for it. Check before citing.
- I found no Tekijänoikeusneuvosto opinion on consultant reports attached to plans. The YM report is the nearest source and it has thesis-level weight.

## Licences: ODbL, OSMF geocoding guideline, CC BY 4.0, HRI, and LLM outputs

### Takeaway
[Interp.] The likely clean structure has three parts: the decision data with OSM-derived coordinates is defensible under the geocoding guideline as non-substantial, the Kerro kantasi extract remains an ODbL Derivative Database that must be offered, and LLM text is best treated as a Produced Work needing a notice. Mixing OSM and non-OSM coordinates, or exposing a general geocoder, weakens that position.

### Cited Findings
- **[Rule]** A Derivative Database includes extracting or re-utilising the whole or a Substantial part of the Contents in a new database. "Substantial" covers quantity or quality, and repeated systematic extraction of insubstantial parts can amount to it. — [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- **[Rule]** A Produced Work is a work "such as an image, audiovisual material, text, or sounds" resulting from using the Contents "via a search or other query". — [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- **[Rule]** 4.3 requires a notice reasonably calculated to make anyone who "uses, views, accesses, interacts with, or is otherwise exposed to" the Produced Work aware of the source and licence. — [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- **[Rule]** 4.4 requires share-alike for a publicly used Derivative Database, and a Derivative Database counts as Publicly Used if a Produced Work created from it is. 4.6 requires offering a machine-readable copy or the alteration file. — [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- **[Rule]** A Collective Database means the Database "in unmodified form" as part of a collection of independent databases. Under 4.5 it need not be licensed under ODbL, but the licence still applies to the ODbL part. — [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- **OSMF geocoding guideline** (endorsed 24 August 2017): it does not treat all geocoding results as Produced Works. A collection of results is not a substantial extract if it contains only names, addresses and/or lat/long, and is not a systematic attempt to gather all or nearly all primary features of a type across a city-sized or larger area. A collection used as a general-purpose geodatabase counts as systematic, however assembled. Results can be stored with third-party data without share-alike effect if not aggregated into a substantial copy. — [OSMF guideline](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Geocoding_-_Guideline)
- Geocoders using OSM data, and applications using them, must credit OpenStreetMap. A group of geocoding results need not keep attribution attached unless it is a Derivative Database. — [OSMF Attribution Guidelines](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines)
- Collective Database Guideline: OSM and non-OSM data stay independent if data for a primary feature type is "either all OSM or all non-OSM within the same regional cut". — [OSMF guideline](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Collective_Database_Guideline_Guideline)
- ML guidance: models trained on substantial OSM extracts must be attributed in documentation, predictions "are not implicated by ODbL", but an overtrained model that recreates the training set may produce a Derivative Database. LLMs and retrieval are not named. — [OSMF Attribution Guidelines](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines)
- OSMF's FAQ treats a tile API as likely a Produced Work, and says recipients can request the underlying data and any Derivative Database. — [OSMF Legal FAQ](https://osmfoundation.org/wiki/Licence/Licence_and_Legal_FAQ)
- Kerro kantasi service terms: "All data in the Service is published as open data" under ODbL; comments and submitted material are CC BY-NC-SA 4.0. — [terms](https://github.com/City-of-Helsinki/kerrokantasi-ui/blob/main/cities/helsinki/i18n/service-info/content.en.md)
- Repo measurements: the geocode cache has 1 220 names, 1 008 located (741 street, 194 district, 70 place, 3 manual, 212 none). The dataset holds 185 hearings, against a count of 401 from the [Kerro kantasi API](https://kerrokantasi.api.hel.fi/v1/hearing/?limit=1).
- HRI metadata lists the zoning index as CC-BY-4.0 ([HRI](https://hri.fi/data/api/3/action/package_show?id=helsingin-asemakaavahakemistokartta-asemakaavahakemisto)). The repository's required credit is "Data ja kartat (c) Helsingin kaupunki, kaupunkimittauspalvelut" ([README](../../../README.md)).

### Inferences
- **Nominatim coordinates:** [Interp.] The cache fits the safe harbour: names and coordinates, derived from decision titles, not a systematic harvest. **A `geocode` MCP tool or a published full street list would undercut that**, since general-purpose use counts as systematic. The 741 street names are worth checking against Helsinki's total. **[Confirm]** for commercial use.
- **Kerro kantasi:** [Interp.] 185 of 401 hearings is likely "Substantial", and filtered plus re-geocoded data is not "unmodified", so treat it as a Derivative Database. Publish it under ODbL, which `data/README.md` already points towards, and offer the full file from the service. Keep it as a separate store so the decisions dataset stays outside share-alike under 4.5.
- **Is the combined DB Derivative or Produced?** [Interp.] The internal store is a collection (Collective, if the parts stay independent and the ODbL part is under ODbL). Each API response is a query result, so plausibly a Produced Work. A bulk `export_all` tool, or pagination allowing full extraction, is Re-utilisation of a database, not a Produced Work, so its output carries ODbL for the Kerro kantasi part.
- **LLM outputs:** [Interp.] "Text... via a search or other query" fits an LLM answer. The server cannot force a client to display a notice, so put `attribution` and `licence` in every tool result, in the server's instructions and on a public page. This is a "reasonably calculated" effort, untested for MCP. CC BY 4.0 is harder, since attribution should accompany reuse, and an LLM may drop it.
- **Migration caution:** Moving geocoding from OSM to City data should be done wholesale per feature type, to stay within the "all OSM or all non-OSM" test. The geocoding guideline itself tolerates a fallback geocoder, so the two guidelines are not fully aligned. **[Confirm]** only if the mix is retained.

### Gaps
- The HRI terms page returned 403 to my fetcher. CC BY 4.0's precise requirements are taken from general knowledge of the licence, not re-read in this session.
- OSMF has no guidance I could find on retrieval-augmented LLM use. The ML guidance concerns training.

## GDPR and Finnish law: re-publication, searchability, removal, erasure and exemptions

### Takeaway
**[Rule]** The City must publish only necessary personal data and remove it from the web when the appeal period ends. **[Interp.]** No provision I read addresses a third-party mirror directly, but we would be an independent controller whose copy defeats that rule, without the City's statutory basis. Public availability is not a free pass. Journalism and research exemptions are unlikely to fit an automated public service.

### Cited Findings
- **[Rule] Kuntalaki 140 §:** the minutes, with appeal instructions, are kept available on the public network unless secrecy rules apply. "Pöytäkirjassa julkaistaan ainoastaan tiedonsaannin kannalta välttämättömät henkilötiedot. Pöytäkirjan sisältämät henkilötiedot on poistettava tietoverkosta oikaisuvaatimus- tai valitusajan päättyessä." — [Act 410/2015, Finlex open data](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@)
- **[Rule] 108 §** applies to municipal notices: 14 days online unless the nature of the matter dictates otherwise, with personal data removed afterwards. **142 §** requires personal data in an administrative court decision notice to be removed when the appeal period ends. **29 §** requires the municipality's web communication to protect privacy and keep secret data off the network. — [Act 410/2015](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@)
- Kuntaliitto says online minutes need to stay up at least 21 days (7+14), or at least 37 days for a kunnallisvalitus (7+30). It recommends removing meeting documents at the latest a year after publication, and keeping personal data online only for the time effective communication requires. — [Kuntalain oikaisuvaatimus, 28.7.2025](https://www.kuntaliitto.fi/laki/muutoksenhaku/kuntalain-oikaisuvaatimus); [Verkkoviestinnän erityiskysymyksiä, 7.8.2025](https://www.kuntaliitto.fi/laki/julkisuus-ja-tietosuoja/verkkoviestinnan-erityiskysymyksia); [Kuntaliitto letter 2017](https://www.kuntaliitto.fi/yleiskirjeet/2017/kunnan-verkkotiedottaminen-seka-henkilotietojen-kasittely-ja-julkisuus-kuntalain)
- **Search-engine guidance:** Kuntaliitto (2017, pre-GDPR) warns that search engines may find text under black-outs, so text must be removed rather than hidden. It also says a municipality that has removed data is not responsible for whether it remains findable through services like Google, citing C-131/12. Web availability counts as disclosure and cannot be supervised, since anyone can access the data. It reports the Ombudsman's view that personal data in minutes does not by itself form a register, though a list within a decision could. — [Kuntaliitto 2017](https://www.kuntaliitto.fi/yleiskirjeet/2017/kunnan-verkkotiedottaminen-seka-henkilotietojen-kasittely-ja-julkisuus-kuntalain)
- An older Ombudsman document, seen only as a search excerpt, says agendas and minutes on municipal sites can show up in search engines, and that the duty to inform alone does not settle web publication. — [tietosuoja.fi PDF](https://tietosuoja.fi/documents/6927448/10594424/Henkil%C3%B6tietojen+luovuttaminen+viranomaisten+henkil%C3%B6rekistereist%C3%A4.pdf/6c212631-26e6-47ae-49a7-45f12e91c5be/Henkil%C3%B6tietojen+luovuttaminen+viranomaisten+henkil%C3%B6rekistereist%C3%A4.pdf?t=1543301307000) (direct fetch returned 403)
- Sipoo removed older minutes because personal data could not be removed individually, and now keeps them online for four years. — [Sipoo](https://www.sipoo.fi/palvelu/esityslistat-ja-poytakirjat/)
- **Observed City practice:** four sampled decision pages from 2017–2024 each contain 3–6 @hel.fi emails and 3–8 phone-like numbers, including general contacts. The one I inspected closely (2021) shows a contact-person block with name, title, phone and email, plus appeal instructions, about five years after the decision. This is a tiny sample, not a policy. (Fetched from paatokset.hel.fi, e.g. [hel-2021-005056](https://paatokset.hel.fi/fi/asia/hel-2021-005056?paatos=f44ce41b-7dd1-4eac-a9c2-4260d8dff677).)
- Attachment names such as "Asunto-Oy Säästökarin muistutus (julkaisuversio)" point to a City publication-version practice. "Muistutukset" and "Mielipiteet" also appear. — [plans_dataset.json](../../../data/plans_dataset.json)
- **[Rule] Julkisuuslaki 16 §** (1999 text): 2 mom. gives a right to a copy in electronic form of public data in a register of an authority's decisions, unless special reasons dictate otherwise; other documents are at the authority's discretion. 3 mom.: personal data from an authority's personal register may be given only if the recipient may lawfully store and use it under data protection rules. — [Act 621/1999, original version](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute/1999/621/fin@). Later amendments were not checked. A [Lakimies article](https://journal.fi/lakimies/article/download/137572/89453/316059) discusses the KHO's reading of 2 mom.
- **[Rule] Data Protection Act 28 §** routes access and disclosure from authority registers to the openness legislation. — [Act 1050/2018](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2018/1050/fin@)
- **[Rule] 4 § 1 kohta** allows Art. 6(1)(e) processing of data on a person's position and tasks in a public body or business, where the aim is in the public interest and proportionate. — [Act 1050/2018](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2018/1050/fin@)
- **[Rule] Journalism and expression, 27 §:** large derogations for processing "ainoastaan journalistisia tarkoituksia varten" or for academic, artistic or literary expression. — [Act 1050/2018](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2018/1050/fin@)
- In C-73/07 the CJEU held that activities on public-document data may be journalistic, but only if solely for journalistic purposes. — [Merlin/CoE](https://merlin.obs.coe.int/article/7340)
- The ECtHR Grand Chamber (2017) found no violation in restricting mass publication of Finnish tax data. It distinguished public access from a public interest "in disseminating en masse such raw data in unaltered form without any analytical input" (§ 175). — [Voorhoof commentary](https://inforrm.org/2017/07/06/case-law-strasbourg-satakunnan-markkinaporssi-oy-and-satamedia-oy-v-finland-no-journalism-exception-for-massive-exposure-of-personal-taxation-data-dirk-voorhoof/)
- **[Rule] Research, 31 §:** derogation from Art. 15, 16, 18 and 21 needs a research plan, a responsible person or group, and use such that data on a specific person is not revealed to outsiders. 4 § 3 kohta is the research basis. — [Act 1050/2018](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2018/1050/fin@)
- **C-439/19** (Grand Chamber, 2021): the GDPR precludes a national rule making penalty-point data publicly available, even as public information. — [eucrim](https://eucrim.eu/documentation/ecj-eu-criminal-law-cases-overview/c-43919/)
- **C-131/12:** a search engine is a controller separate from the publisher, can be required to remove results even when the original publication is lawful, and cannot rely on the journalism exception. — [Hunton](https://huntonak.com/privacy-and-information-security-law/eu-court-justice-upholds-right-erasure-google-search-case); [5RB](https://www.5rb.com/cjeu-finds-google-must-remove-certain-search-results/)
- **EDPB Opinion 28/2024** treats public availability as one factor in the legitimate-interest balance, says web scraping carries specific risks, and lists mitigations such as excluding some publications or data categories. — [EDPB, Finnish text, paras 104–105](https://www.edpb.europa.eu/system/files/documents/2025-05/edpb_opinion_202428_ai-models_fi.pdf). EDPB guidance on delisting says it applies to name-based searches, and the information stays available under other terms. — [Guidelines 5/2019 summary](https://gvzh.mt/insights/guidelines-published-edpb-right-to-be-forgotten/)
- **[Rule] GDPR Art. 17(3)** limits erasure where processing is necessary for freedom of expression and information, among others. **Art. 5(1)(d)** requires inaccurate data to be erased or rectified without delay. — [Art. 17](https://gdpr-info.eu/art-17-gdpr/); [Art. 5](https://gdpr-info.eu/art-5-gdpr/)

### Inferences
- **What must go offline:** [Interp.] 140 § binds the City, but a re-publisher relying on legitimate interest must justify keeping what the City must remove. The workable rule is to index only the non-personal parts of a decision from day one, so there is nothing to remove. If names are ever retained, a time limit tied to removal at source is the minimum. **[Confirm with DPO]**
- **Officials versus private persons:** [Interp.] Officials acting in role are lower risk (cf. 4 § 1 kohta), though contact details are unnecessary for the service's purpose. Applicants, objectors and property owners are higher risk. Allowing a query like "what has person X objected to" creates a new profile that doesn't exist on the City's site.
- **LLM effects:** [Interp.] The MCP operator cannot recall text once it is in a client's chat history or a client's cache. This raises the importance of minimising data before serving. It also makes `retrieved_at` and short cache lifetimes worthwhile.
- **Bulk data:** [Interp.] 16 § 2 mom. is a real alternative to scraping, if Ahjo is a "register of decisions". 3 mom. would then require us to show lawful use, which makes the DPIA-style documentation useful in both directions.
- **Exemptions:** [Interp.] 27 § is unlikely to cover an automated, unedited service, per the ECtHR's "analytical input" reasoning. It could cover a separate editorial project. Research (4 § 3, 31 §) doesn't fit open public serving because it bars revealing data on specific persons. So plan on Art. 6(1)(f). A DPIA is prudent, though I did not establish that it is mandatory.
- **Minimum erasure route:**
  1. A public contact address and a privacy notice naming the controller.
  2. An identity check limited to what is needed.
  3. A response within the GDPR's time limit.
  4. Suppression by decision ID that survives re-scrapes, which the daily job would otherwise undo.
  5. A log kept without unnecessary personal data.
  6. Removal also from git history, since `data/` is committed publicly. This is an easily overlooked trap.
  7. Referral to the City for the original.
  8. A note that the Ombudsman is the supervisory authority.

### Gaps
- I found **no current Ombudsman decision** on third-party re-publication or LLM indexing of municipal decisions, and no tietosuoja.fi LLM guidance. The tietosuoja.fi material I reached is pre-GDPR or an excerpt. Conclusions here rest on Kuntalaki text, Kuntaliitto and EU authority.
- I found no Helsinki privacy notice for Ahjo or paatokset.hel.fi, and no City statement of its retention practice. The DPO address published by the City is tietosuoja(a)hel.fi, per the [City's privacy page](https://www.hel.fi/fi/paatoksenteko-ja-hallinto/tietoa-helsingista/tietosuoja-ja-tiedonhallinta/tietosuoja) as summarised by search, not read directly.
- Not verified in this session: C-136/17 *GC*, C-184/20 *OT*, KHO's Satakunnan judgment number. GDPR Art. 14 text could not be extracted from my fetch; Art. 14(5)(b) (disproportionate effort) is from general knowledge. **[Confirm]**

## Helsinki's own terms: official API, open-data policy, scraping and contacts

### Takeaway
There is **no public official Ahjo API today that I could find**. OpenAhjo is closed, a replacement is "planned" with no date, and the City's real Ahjo API requires authentication. The Elasticsearch proxy is open but is a site backend, and I found no terms permitting or forbidding reuse. Ask the City in writing.

### Cited Findings
- **OpenAhjo:** the HRI and avoindata.fi notes (12/2024) say the API, launched in 2015, reached the end of its technical lifecycle and has closed, and a replacement open-data API is planned with no estimate. — [HRI dataset page, seen as a search excerpt](https://hri.fi/data/en_GB/dataset/helsingin-kaupungin-asianhallintajarjestelma-ahjon-rajapinta); [avoindata.fi](https://www.avoindata.fi/data/en_GB/dataset/helsingin-kaupungin-asianhallintajarjestelma-ahjon-rajapinta)
- The GitHub repository is archived. — [openahjo](https://github.com/City-of-Helsinki/openahjo)
- **Probes on 2026-11-02:** `dev.hel.fi` refused connections from my network. `api.hel.fi/paatos/v1/` returned 404. HRI's CKAN API gives an authorization error for the OpenAhjo dataset and returned 0 results for "ahjo". These are point-in-time checks, and the first could be a local network matter. The stale [dev.hel.fi page](https://dev.hel.fi/apis/openahjo/) still recommends OpenAhjo, as seen in search results.
- **City's real API:** "The majority of the site's content come from AHJO API" and the site has "a proxy for querying AHJO API directly (requires authentication)", along with APIs for JavaScript apps (open endpoints). Its details sit in a City Confluence I did not access. — [helsinki-paatokset README](https://github.com/City-of-Helsinki/helsinki-paatokset)
- **Elasticsearch proxy:** City code calls the service `PublicElasticProxy`. — [helfi-api-base EnvironmentResolver](https://github.com/City-of-Helsinki/drupal-module-helfi-api-base/blob/main/src/Environment/EnvironmentResolver.php). My probe: `_search` is open with `access-control-allow-origin: *`, no rate-limit headers were seen on a single request, and `_cat/indices` and `_mapping` return 404, so it is deliberately filtered. Documents include full `decision_content` and `decision_motion` HTML, which makes it a tempting full-text source.
- **robots.txt:**
  - [paatokset.hel.fi](https://paatokset.hel.fi/robots.txt) disallows search and filter URLs (`/search/`, `?from=`, `?to=`, `?category=`, `?dm=`, `/fi/asia?*s=*`), but not ordinary decision URLs. No crawl-delay or AI-specific rule.
  - [ahjojulkaisu.hel.fi](https://ahjojulkaisu.hel.fi/robots.txt) is `Disallow: /`, and a sampled PDF sends `x-robots-tag: noindex`.
  - [www.hel.fi](https://www.hel.fi/robots.txt) disallows some `/static/mirror*` paths; I saw no rule on `/static/public/hela`.
  - [kerrokantasi.api.hel.fi](https://kerrokantasi.api.hel.fi/robots.txt) has none (404).
- Drawing hosts in the dataset: ahjojulkaisu 857, www.hel.fi 724, none 146. — [plans_dataset.json](../../../data/plans_dataset.json)
- **Terms:** I found no paatokset.hel.fi terms-of-use page. Links matching terms or privacy in the sampled page HTML showed only an accessibility statement. Kerro kantasi has explicit ODbL terms, and WFS zoning data has CC BY 4.0, so the decisions service is the gap.
- Successor candidate for the data model: [6aika/paatos](https://github.com/6aika/paatos). Status unclear.

### Inferences
- [Interp.] Absence of terms is not permission. Decision text being copyright-free (9 §) and pages being public supports reading, but not necessarily use of the backend at volume. `robots.txt` isn't law but is the clearest signal available, and it fits the City's 140 § concern: it keeps attachment PDFs out of search indexes while keeping them linkable. A service that makes them searchable would work against this signal.
- **Migration:** none possible today unless the City grants access to the authenticated API, which is worth asking about. Design a source-adapter layer so that the proxy can be replaced.
- **Rate limiting:** apply our own limits even though none is advertised. Serve from our own store, never pass an LLM query through to the proxy.
- **Contacts to try:**
  1. City's DPO, tietosuoja(a)hel.fi, on 140 § and re-publication.
  2. HRI (via the [contact page](https://hri.fi/fi/yhteystiedot/); no address extracted) on the replacement API and terms.
  3. A public issue or discussion on [helsinki-paatokset](https://github.com/City-of-Helsinki/helsinki-paatokset) on proxy stability.
  4. Kirjaamo for a formal 16 § request.

  Ask specifically: may the proxy be used by third parties and at what rate? Is there a timeline for the replacement API? May we get authenticated Ahjo access? What is the attachments' licence? What retention rule applies?

### Gaps
- No statement either way from the City on third-party use of the proxy, and no announced rate limits. The HRI page text is from search excerpts because my fetcher received 403. Internet Archive terms were not reviewed; its use here (meeting lists only) looks low risk.

## Nominatim policy and alternatives

### Takeaway
**[Rule]** A public service that geocodes on LLM queries through public Nominatim is at best marginal and likely violates the policy at any meaningful use. Keep the present batch model or replace it with the City's CC BY address data.

### Cited Findings
- **[Rule]** Maximum 1 request/s, a valid identifying User-Agent or Referer, visible attribution, and results "must be cached". Scripts running over a day or at regular intervals are limited to 4 requests per minute. Auto-complete and systematic queries are forbidden. — [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)
- **[Rule]** End-user-triggered use "is ok, provided that your number of users is moderate", and "the sum of traffic by all your users should not exceed the limits". Apps must be able to switch service at OSMF's request. — [same](https://operations.osmfoundation.org/policies/nominatim/)
- **[Rule] LLM clause:** "LLMs may only suggest this service, if they prominently point to this usage policy and explain the restrictions of use to the user." The public API "must not be built into, offered through, suggested by, or automatically generated by no-code, low-code, or vibe-coding platforms as a generic geocoding, address lookup, place search, or map search service." Use is only permitted where the developer made a "deliberate, informed decision" and is directly responsible for compliance. — [same](https://operations.osmfoundation.org/policies/nominatim/)
- Repo's current method (≤4/min, published cache, identified agent) lines up with this. — [README](../../../README.md)
- **City address data:** Helsingin osoitteet, CC-BY-4.0, maintained by Kaupunkimittauspalvelut, names in Finnish and Swedish. Metadata last modified 2024-03-21. — [HRI](https://hri.fi/data/api/3/action/package_show?id=helsingin-osoiteluettelo). Also `helsingin-nimisto` and `seudullinen-osoiteluettelo`, both CC-BY-4.0, per [HRI search](https://hri.fi/data/api/3/action/package_search?q=osoiteluettelo).
- **Servicemap:** live test `api.hel.fi/servicemap/v2/search/?q=Neptunuksenkatu&type=address` returned address coordinates (Neptunuksenkatu 1 about 80 m from the dataset's street point, by my estimate). — [servicemap](https://api.hel.fi/servicemap/v2/search/?q=Neptunuksenkatu&type=address&page_size=1)
- **Digitransit:** registration and API key required, CC BY 4.0 with date-of-retrieval credit, "as it is", and may apply rate limits. It states ODbL covers OSM-based data that "covers in practice part of routing, geo-coding, and map-API data". — [Digitransit terms](https://digitransit.fi/en/developers/apis/7-terms-of-use/)

### Inferences
- **Recommended:** resolve new names against the local City address and name datasets, falling back to a daily batch through Nominatim, or to a self-hosted instance. Own Nominatim removes the usage policy issue but not ODbL.
- [Interp.] The service's tools should accept filters such as district or plan type. It should have **no free-text geocode tool**, as an LLM agent could loop and trigger forbidden systematic use, and it would also damage the licence position.
- City address data would likely also improve precision and avoid ODbL for coordinates, though see the migration caution above.

### Gaps
- Servicemap's licence and rate terms were not found. Digiroad and DVV address data terms were not found in this session. Digiroad targets road network geometry, so it may help for street extents, but this is unverified.

## EU AI Act, liability, and appeal deadlines

### Takeaway
[Interp.] A deterministic MCP data server is probably not an "AI system" and is not high-risk, but adding generated summaries could trigger Art. 50 duties. Liability risk mainly comes from wrong facts on deadlines and legal status, and the deadline rules are complex enough that the service should refuse to state one.

### Cited Findings
- AI system: a machine-based system that "infers, from the input it receives, how to generate outputs". Provider and deployer definitions apply. — [AI Act Art. 3](https://artificialintelligenceact.eu/article/3/)
- **[Rule] Art. 50:** (1) providers must design AI systems interacting with people so they know it. (2) Providers of generative systems must mark outputs in a machine-readable way. (4) Deployers must disclose AI-generated text published to inform the public on matters of public interest, unless it has had human review or editorial control with someone holding editorial responsibility. — [AI Act Service Desk](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50)
- **Timing:** law-firm sources report Art. 50 applying from 2 August 2026, with legacy generative systems' marking grace until 2 December 2026, Commission guidelines adopted on 20 July 2026, and Omnibus Regulation (EU) 2026/1744 in force 27 July 2026, moving Annex III high-risk duties to 2 December 2027. Fines under Art. 50 run up to €15m or 3% of turnover. — [Goodwin](https://www.goodwinlaw.com/en/insights/publications/2026/08/alerts-technology-dpc-eu-ai-act-transparency-obligations-now-in-force); [Jones Walker](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html). I did not read the Official Journal text.
- Annex III point 8(a) concerns systems helping a judicial authority research and interpret facts and law. — [AI Act Service Desk FAQ](https://ai-act-service-desk.ec.europa.eu/fr/node/468)
- **Product liability:** Directive 2024/2853 covers software, including stand-alone software and AI systems. Pure information is excluded, as is non-commercial free and open-source software. Transposition is due by 9 December 2026. Finland published a draft bill in February 2026, with comments to March 2026, and will not include the development-risk defence. — [CMS](https://cms.law/en/int/publication/the-new-eu-product-liability-directive-eu-2024-2853); [CMS update](https://cms-lawnow.com/en/ealerts/2025/05/transposition-time-netherlands-finland-and-sweden-update-on-the-eu-member-states-adoption-of-the-new-product-liability-directive); [Reed Smith, 8 Sept 2026](https://www.reedsmith.com/articles/eu-product-liability-directive-where-things-stand-with-member-state-transposition/); [Bird & Bird](https://www.twobirds.com/en/insights/2025/finland/expansion-of-the-definition-of-product-under-the-revised-product-liability-directive--the-finnish-pe); [Faegre Drinker, June 2026](https://www.faegredrinker.com/en/insights/publications/2026/6/transposing-the-eus-new-product-liability-directive-a-member-state-progress-report)
- **[Rule] Appeal rules, Kuntalaki:**
  - 134 §: rectification claim against committee decisions.
  - 135 §: municipal appeal to the administrative court against council decisions and rectification outcomes; grounds must be stated before the appeal period ends.
  - **136 §: no rectification claim or appeal against a decision concerning only preparation or implementation.**
  - 137 §: only a party or a municipal member may claim; a further appeal is limited to those who made the claim, with a stated exception.
  - **138 §: 14 days for rectification, 30 days for appeal, both from notification.**
  - **140 §: a member is deemed notified seven days after the minutes are online.**
  — [Act 410/2015](https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/2015/410/fin@)
- Parties have different start rules: 7 days after posting a letter, the third day after an electronic message. The day of notification isn't counted, weekends and holidays shift the last day, and filing is due before closing time. — [Kuntaliitto](https://www.kuntaliitto.fi/laki/muutoksenhaku/kuntalain-oikaisuvaatimus)
- Sampled Helsinki decision [hel-2021-005056](https://paatokset.hel.fi/fi/asia/hel-2021-005056?paatos=f44ce41b-7dd1-4eac-a9c2-4260d8dff677) has a decision-specific 30-day appeal text, with its own right-to-appeal wording, showing that routes vary between decisions.

### Inferences
- **Is it regulated?** [Interp.]
  - Retrieval-only server: likely not an AI system, so not a provider. The LLM vendor and client deployer hold Art. 50 duties. Semantic search with embeddings is a grey area worth noting. **[Confirm]**
  - Publishing auto-generated summaries on a page or in tool output: Art. 50(2) and (4) become live; human review or labelling is the mitigation.
  - Not Annex III point 8: a citizen tool not used by a judicial authority. This could change if sold to courts.
- **Appeal danger, concretely.** A naive answer "14 days from the decision date" could be wrong in at least five ways:
  1. The route differs (14 versus 30 days).
  2. The clock starts from notification, not `date`, and our data has **no publication date field**, only a meeting date.
  3. Members and parties have different start rules.
  4. The 7-day presumption can be rebutted, and calendar rules shift the end date.
  5. **47.9% of records are "proposal"**, and a preparatory decision can't be appealed at all under 136 §, so the right action may be a later body's decision.

  Missing the period usually loses the right, and new grounds cannot be raised afterwards (135 §). Tool design: `appeal_info` returns the link to the original "Muutoksenhaku" section and a fixed sentence, and nothing else.
- **Property purchases:** [Interp.] Approximate location, a stage heuristic, no in-force status and no later-stage tracking make false reassurance likely. A later Council decision or an administrative court ruling may not be reflected. Terms of use should exclude reliance, but a disclaimer may not fully defeat negligence or consumer claims.
- **Liability allocation:** free, non-commercial and open source may be outside the new product liability directive, and "pure information" is excluded, but a paid service may not get those exclusions. Whether a data API counts as software or as information is untested. **[Confirm]**

### Gaps
- Status of Finland's government bill on product liability is unknown. I did not review the Tort Liability Act (412/1974) on pure economic loss, the land-use act's appeal provisions (I could not retrieve 132/1999 or confirm 188 §), or the DSA. All need a lawyer.
- No guidance found on whether an MCP server is an AI system or a component.

## Data quality: measured risks and LLM amplification

### Takeaway
**61.1% of records have at least one of: district-level location, stage "other", no drawing, or empty summary.** Accuracy is **not measured at all**, because the 100-record sample is unreviewed. This is acceptable with pin-level caveats on a map, but not yet for a tool whose output is restated confidently.

### Cited Findings
All figures come from read-only checks run on 2026-11-02 against [plans_dataset.json](../../../data/plans_dataset.json) (`generated` 2026-11-01), [umap/*.geojson](../../../data/umap/) and [quality_sample.csv](../../../data/quality_sample.csv). They match the [README table](../../../README.md).

| Measure | Result |
|---|---|
| Records / unlocated | 1 727 / 105 (5.7% of 1 832) |
| District-centroid location | **438 / 1 727 = 25.4%** (street 68.3%, place 6.0%, manual 0.3%) |
| Records sharing an exact coordinate | 1 230 / 1 727 = 71.2% (816 distinct points; up to 22 at one point) |
| Stage | proposal 47.9%, approved 41.4%, **other 173 = 10.0%**, returned 0.7% |
| Stage "other" by period | 166 of 173 before June 2017 |
| Pins offset (per-type GeoJSON) | **870 / 1 807 = 48.1%**; median 55 m, p90 96 m, max 160 m; 80 over 100 m. Dataset coordinates are unaffected |
| Missing drawing | **146 / 1 727 = 8.5%**; 120 of them in 2017–2018 |
| Empty summary | **734 / 1 727 = 42.5%**; 733 of them in 2013–2017 |
| Truncated summary (ends "…", max 320 characters) | 462 / 1 727 = 26.8%, including 229 "approved" |
| Stage assigned from title only (empty summary, not "other") | **569 / 1 727 = 32.9%**, including 220 of 715 "approved" |
| "Proposal" whose summary contains hyväksyi/päätti hyväksyä | 27 (candidates for checking, not confirmed errors) |
| Summaries or headings mentioning lainvoima/voimaan | 54 = 3.1% |
| Zoning (asemakaava) stage | proposal 628, approved 113, other 30, returned 4, of 775 |
| Kerro kantasi | 185 hearings: 165 area, 9 street, 7 place, 4 district; 18 with no drawings |
| Role + person-name pattern in summaries | 0 (crude regex, so not evidence of no names) |
| Provenance fields in records | No publication date, legal status, retrieval time, source or licence field |

**quality_sample.csv:** all 100 rows are empty in `type_ok`, `stage_ok`, `drawing_ok`, `location_ok` and `notes`. Its mix is 32 district (versus 25.4% overall), 12 stage-not-stated (10.0%) and 9 no-drawing (8.5%), so it is not badly skewed, with district somewhat over-represented. The README confirms it is unreviewed, and that automated checks can't tell if a pin is on the right street. — [README](../../../README.md)

**Stage is a keyword heuristic, and stage "other" means the title and summary don't say.** — [README](../../../README.md)

**Illustrative record:** the first dataset record has heading "Kaupunkiympäristölautakunnan esitys...", date 05.09.2017, a summary describing a *2016 predecessor committee* action, `map_url: null`, district-level location and stage "proposal". An LLM might blend these into one wrong statement about what happened when.

### Inferences
**Which errors get worse under LLM restatement** (my assessment, ranked):

| Error type | On the map | When an LLM restates it | Severity |
|---|---|---|---|
| `approved` read as legally valid; `proposal` read as decided | Filter label | "The plan has been approved", dropping "by the committee" | **Highest** |
| Appeal status or deadline inferred | Not shown | A confident specific date | **Highest** |
| Stale outcome: later Council or court decision absent | Old pin looks old | Present tense, no timing | High |
| Truncated summary (26.8%) | "…" is visible | Model completes the thought or treats it as complete | High |
| Title-only stage (32.9%) | Hidden | Presented with the same confidence as text-based | High |
| District centroid (25.4%) | Visibly coarse if zoomed | "Located at [coordinates]", or an inference about a nearby property | High for property questions |
| Absence read as negative ("no plan affects X") given keyword filter, 5.7% unlocated, 2013 floor | Empty map is ambiguous | "There are no plans for this street" | High |
| Wrong drawing link (unmeasured) | User sees the PDF | Model summarises the wrong document | Medium; high with PDF ingestion |
| Pin offset | "pin offset N m" shown | Removable by serving true points | Low after fix |
| Empty summaries | Blank | Model invents from the title | Medium |

**Mitigations in tool output (provenance fields).** These are proposals, not existing fields.

```json
{
  "record_id": "...",
  "official_source": {"decision_url": "...", "drawing_url": "...", "authoritative": true},
  "retrieved_at": "2026-11-01", "source_system": "paatokset-es|hela|kerrokantasi",
  "stage": {"value": "proposal", "method": "keyword_heuristic", "basis": "title_only|title_and_summary",
            "meaning": "committee stage only; NOT legal validity"},
  "legal_status": "unknown",
  "appeal": {"status": "not_provided", "see": "<decision_url>",
             "instruction": "Do not state or compute a deadline; refer to the original decision."},
  "location": {"lat": 0, "lon": 0, "precision": "street|place|area|district",
               "meaning": "point on named street or district centroid; not plan extent",
               "method": "geocoded_from_title"},
  "summary": {"text": "...", "truncated": true, "empty": false},
  "completeness": {"plan_detection": "keyword filter; may miss plans",
                   "absence_is_not_evidence": true, "coverage_from": 2013},
  "quality": {"manual_review": "not_performed"},
  "attribution": ["City of Helsinki (decisions)", "(c) OpenStreetMap contributors, ODbL (coordinates)"],
  "notice": "Unofficial, experimental, independent of the City of Helsinki. Verify against the linked document."
}
```

- Field names that carry their own meaning (e.g. `stage_committee_only`) are more likely to survive restatement than a footer. [Interp.] A server-level instruction helps, but clients can ignore it, so it complements field design and does not replace it.
- **Before launch:**
  1. Complete the 100-row review. With n=100, zero errors would bound the true rate at roughly 3% (95%), and 10 errors imply about 5–17%. Stratify by period and by stage, since 2013–2017 data is much thinner.
  2. Add `basis` and `truncated`.
  3. Add a real publication date, where one is available.
  4. Serve true points, not spread ones.
  5. Build a small regression set of questions, checking that clients do not emit deadlines or "valid".

### Gaps
- True accuracy of type, stage, drawing and location is **unknown**, not merely unstated. I did not review the 100 records, as the task was limited to read-only checks of existing values.
- I measured personal data only by a crude regex on summaries, plus a sample of four decision pages. Prevalence of private persons' names in full decision text and attachments is unmeasured, and should be sampled before any full-text decision. The proxy offers `decision_content`, which would make this practical.
- I have no measurement of how often LLM clients preserve caveat fields, and found no study specific to this.
