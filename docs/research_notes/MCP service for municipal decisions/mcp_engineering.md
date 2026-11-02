# MCP engineering: building and hosting a public read-only MCP server for lautakuntamuistiot

Researched 2026-11-02. All prices were read that day. "Local measurement" marks something I ran on this repository's real data in a scratch directory (MacBook, Python 3.14.3 with `mcp` 2.3.0, and system Python with SQLite 3.51.0). Those are single-machine indications, not benchmarks. The scripts are outside the repository and nothing in it changed except this note.

## What is the current MCP specification and what changed recently?

### Takeaway
The current revision is **2026-07-28**, and it is a breaking redesign: no handshake and no sessions, so each request stands alone. That suits a read-only server well, but dated tutorials and older clients still assume the 2025 model, so the server should serve both eras on one endpoint.

### Cited Findings
- The current protocol version is 2026-07-28. Version strings mark the last backwards-incompatible change — [Versioning](https://modelcontextprotocol.io/specification/versioning)
- The release was announced on 28 July 2026, as "transforming from a bidirectional stateful protocol into a request/response stateless protocol". Any request can land on any instance behind a round-robin load balancer without shared storage — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- **Removed:** protocol sessions and `Mcp-Session-Id`, the `initialize` handshake, `ping`, `logging/setLevel`, the HTTP GET stream, `resources/subscribe`, and SSE resumability via `Last-Event-ID` — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- **Added:**
  - a mandatory `server/discover` RPC;
  - per-request `_meta` carrying protocol version, client info and capabilities;
  - `subscriptions/listen` for change notifications;
  - Multi Round-Trip Requests (`resultType: "input_required"`), which replace server-initiated elicitation and sampling — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- **Required headers:** every POST must carry `MCP-Protocol-Version` and `Mcp-Method`. `Mcp-Name` is also required for `tools/call`, `resources/read` and `prompts/get`. A mismatch with the body returns 400 with error `-32020`. This lets gateways route and rate limit without parsing bodies — [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
- **Caching:** `tools/list`, `prompts/list`, `resources/list`, `resources/read` and `resources/templates/list` must return `ttlMs` and `cacheScope`, and servers SHOULD order tools deterministically to help prompt caching — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- **Transports:** Streamable HTTP is the remote transport. HTTP+SSE has been deprecated since 2025-03-26 and new implementations SHOULD NOT adopt it — [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
- **Conflict on the SSE timeline:** the announcement describes a year-long offramp ([blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)), while the registry says earliest removal is three months after SEP-2596 reaches Final ([Deprecated features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated))
- **Deprecated, earliest removal in the first revision on or after 2027-07-28:** Roots, Sampling, Logging and Dynamic Client Registration (replaced by Client ID Metadata Documents) — [Deprecated features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)
- **Structured output:**
  - `structuredContent` may be any JSON value and must conform to `outputSchema` if one is declared.
  - A tool returning it SHOULD also return serialized JSON in a text block.
  - Input errors the model can fix belong in a result with `isError: true`.
  - Servers MUST validate inputs, rate limit invocations and sanitize outputs — [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
- **Error code change:** resource-not-found moved from `-32002` to `-32602` — [Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
- **Era compatibility:** legacy client plus modern-only server fails, and legacy clients have no fall-forward mechanism. A dual-era server may serve both on the same endpoint — [Versioning and Compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning)
- **Extensions:** MCP Apps (`io.modelcontextprotocol/ui`), Tasks, Skills over MCP and two auth extensions are optional and negotiated through capabilities — [Extension matrix](https://modelcontextprotocol.io/extensions/client-matrix)
- **MCP Apps:** a tool's `_meta.ui.resourceUri` points at a `ui://` HTML resource that the host renders in a sandboxed iframe. Named hosts include Claude, Claude Desktop, VS Code Copilot, Microsoft 365 Copilot and Goose — [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview)
- **Registry:** still in preview, with breaking changes or data resets possible before general availability — [Registry](https://modelcontextprotocol.io/registry/about)
- **Roadmap (22 Aug 2026), no dates given:** a Server Card working group on `.well-known` metadata, "progressive discovery" of tools, and a standard contract for tool results — [Roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)

### Inferences
- Stateless operation removes the main historical cost of hosting MCP (sticky sessions and shared stores). A read-only dataset server now looks like an ordinary JSON-over-POST web service.
- Do not build on sampling, roots, subscriptions, tasks or elicitation. The server needs none of them.

### Gaps
- I did not read every SEP. The changelog is the basis, and the [GitHub comparison](https://github.com/modelcontextprotocol/specification/compare/2025-11-25...2026-07-28) has the full diff.
- The per-client cells of the extension matrix came back blank through my fetch tool, so I rely on the prose host list above.

## Which clients support remote servers, what do they require, how does a non-technical user connect, and what do directories require?

### Takeaway
Anonymous remote servers work today in Claude, ChatGPT (paid plans at least), VS Code, Cursor and Antigravity/Gemini CLI, so **no OAuth is needed**. Claude is the easiest route for ordinary users because even the Free plan gets one custom connector. Directory listing is feasible, but the "experimental" labelling may clash with OpenAI's rules.

### Cited Findings

| Client | Remote and anonymous? | How a user connects | Notes |
|---|---|---|---|
| Claude (web, Desktop, mobile, Cowork) | Yes, "No sign in" option | Customize > Connectors > + Add > Add custom connector, then name and URL | Free, Pro, Max, Ultra, Team and Enterprise. Free is limited to one custom connector. On Team/Enterprise an Owner adds it — [Claude help](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp) |
| Claude Code | Yes | `claude mcp add --transport http <name> <url>` | Warns above 10,000 tokens, caps at 25,000 by default, and saves text results over 50,000 characters to a file — [Claude Code docs](https://code.claude.com/docs/en/mcp) |
| ChatGPT | Yes, developer mode lists OAuth, none or mixed ([search result](https://developers.openai.com/api/docs/guides/developer-mode), page not fetchable) | chatgpt.com/plugins > plus button > Add custom MCP server, then accept a risk warning | Public HTTPS, streamable HTTP, typically `/mcp` — [OpenAI](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt). See plan caveat below |
| VS Code / Copilot | Yes | Command Palette > MCP: Add Server > HTTP, or the gallery via `@mcp` | Prompts and resources are supported, MCP Apps experimental — [VS Code](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) |
| Copilot in other IDEs | Yes | `mcp.json` or the GitHub MCP Registry | The org policy is off by default for Business and Enterprise. Prompts and resources are documented only for VS Code — [GitHub docs](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/extend-copilot-chat-with-mcp) |
| Cursor | Yes | `url` in `mcp.json` or the Marketplace | Tools, prompts, resources, roots, elicitation, Apps — [Cursor](https://cursor.com/docs/context/mcp) |
| Gemini CLI | Yes | `httpUrl` in config, or `gemini mcp add --transport http` | The page says it was replaced by Antigravity CLI on 18 June 2026. Tools become `mcp_{server}_{tool}`, truncated at 63 characters. Avoid underscores in server names. `$schema` and `additionalProperties` are stripped — [Gemini CLI](https://geminicli.com/docs/tools/mcp-server/) |

- **Claude limits on hosted surfaces:** about 150,000 characters per tool result and 240 seconds per call. Resource subscriptions, sampling and "advanced or draft capabilities" are not supported — [Build an MCP server for Claude](https://claude.com/docs/connectors/building/index.md)
- **Claude's network path:** Claude connects from Anthropic's cloud, not the user's device, with traffic from `160.79.104.0/21` — [Authentication for connectors](https://claude.com/docs/connectors/building/authentication)
- **ChatGPT plan caveat:** a search result for the developer mode page lists "Pro, Plus, Business, Enterprise, and Education accounts on the web" and SSE or streaming HTTP — [OpenAI, via search](https://developers.openai.com/api/docs/guides/developer-mode). That URL returned 404 when I fetched it, and the help-center article returned 403, so this is unconfirmed
- **ChatGPT `search` and `fetch`:** for company knowledge and deep research, a server implements read-only `search` (single query string, returning `results` with `id`, `title`, `url`) and `fetch` (`id`, `title`, `text`, `url`, optional `metadata`). Citations are created only when `url` is non-empty — [OpenAI MCP docs](https://developers.openai.com/api/docs/mcp/). The same page's example uses an `/sse/` endpoint, which conflicts with the `/mcp` streamable guidance above

**Directories**

- **Anthropic Connectors Directory** — [Submission](https://claude.com/docs/connectors/building/submission) and [review criteria](https://claude.com/docs/connectors/building/review-criteria)
  - Any paid Claude plan can submit.
  - Needs an HTTPS URL, a `title` and `readOnlyHint` on every tool, documentation URL, privacy policy URL, support contact and icon.
  - No authentication is accepted for public data.
  - Tool names at most 64 characters. Generic errors fail review. No dumping a whole database when a summary was asked for.
  - Descriptions must not instruct Claude how to behave.
  - Automated scan, then listed as "Community" by default.
- **Anthropic's test-credential rule:** credentials are listed as "required", which reads oddly for an authless server, and "the MCP server domain should match your service" — [review criteria](https://claude.com/docs/connectors/building/review-criteria)
- **OpenAI app directory** — [Submission guidelines](https://developers.openai.com/apps-sdk/app-submission-guidelines)
  - Verified individual or organization.
  - Published privacy policy even without auth.
  - Every tool explicitly sets `readOnlyHint`, `destructiveHint` and `openWorldHint`.
  - No precise location requests, and no internal IDs or telemetry unless the query needs them.
  - The app must not be presented as a trial or demo.
- **Official MCP Registry**
  - Metadata only. Verifies namespace ownership via GitHub, DNS or HTTP. Delegates security scanning to others.
  - Meant for aggregators, not for hosts to consume directly — [Registry](https://modelcontextprotocol.io/registry/about)
  - Remote servers use `remotes` with `type: streamable-http` — [Remote servers](https://modelcontextprotocol.io/registry/remote-servers.md)
  - Published with `mcp-publisher`, and can be automated from GitHub Actions — [Quickstart](https://modelcontextprotocol.io/registry/quickstart)
  - The `/v0.1/servers` endpoint returned HTTP 200 when I called it.

### Inferences
- The repository's namespace would be `io.github.kpkoskinen/<name>`, or a DNS namespace if a domain is bought. The registry adds discoverability at almost no cost, and its preview status matters little because publishing can be repeated.
- User instructions should lead with Claude and ChatGPT, in Finnish, with screenshots. Team and Enterprise users need their Owner, which is a real barrier for a city employee on a managed workspace.
- Keep the honest "experimental" warning in tool output, but check it against OpenAI's "not a trial or demo" rule before submitting. Describe it as "an independent, automatically extracted dataset; verify against the linked originals".
- Since Claude has no free-plan barrier for one connector, while ChatGPT's free-plan status is unconfirmed, the launch should not depend on ChatGPT.

### Gaps
- Consumer **Gemini app**, **Mistral Le Chat** and **Microsoft Copilot Studio**: I only found a third-party registry describing custom connectors ([skillsplayground](https://skillsplayground.com/connectors/com-branderux/)), with boilerplate text. Treat these as unverified.
- **Which protocol era hosted clients speak.** I found no vendor statement that Claude or ChatGPT send 2026-07-28 requests. Claude's docs still cite the 2025 authorization revisions ([Claude](https://claude.com/docs/connectors/building/index.md)), which concerns auth rather than transport.
- ChatGPT free-plan access and any EU/EEA limits are unconfirmed. One [developer blog](https://www.getdrio.com/blog/chatgpt-app-submission-gotchas) reports undocumented EU data-residency blocks on submission. It is a single unverified source.

## Which frameworks are appropriate, and how should the dependency be isolated from the stdlib-only rule?

### Takeaway
Use the **official Python SDK (`mcp` 2.x)** as a thin adapter over a **stdlib-only query core**, in a separate, separately pinned deployment unit. The scrapers and daily job keep their zero-dependency guarantee, and the query logic stays testable without any SDK.

### Cited Findings
- **Python SDK:** `mcp` 2.3.0 was released 2026-10-02, and v1.30.0 is still maintained (2026-09-07). PyPI metadata says `requires-python >=3.10` ([PyPI](https://pypi.org/project/mcp/)), while the docs say "Python 3.11+" ([SDK docs](https://py.sdk.modelcontextprotocol.io/)). These conflict, so target 3.12 as `update-data.yml` already does.
- **v2 breaking change:** `FastMCP` was renamed `MCPServer`, and importing `mcp.server.fastmcp` raises `ModuleNotFoundError`, so most tutorials on the web are now wrong — [Migration guide](https://py.sdk.modelcontextprotocol.io/migration/)
- **Both eras:** one `streamable_http_app()` serves both, routed by the protocol version header. `stateless_http=True` affects only the legacy leg, which loses server-to-client channels. "Use stateless mode only if your tools never call back into the client", which holds here. Without it, legacy sessions live in a per-process dict and need sticky routing with more than one worker — [Serving legacy clients](https://py.sdk.modelcontextprotocol.io/run/legacy-clients/)
- **Tier 1 SDKs updated to 2026-07-28:** TypeScript, Python, Go, C#. Rust is in beta — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- **FastMCP (standalone):** 4.1.5 released 2026-11-01, Apache-2.0, with frequent releases — [PyPI](https://pypi.org/project/fastmcp/). Stateless mode is `mcp.http_app(stateless_http=True)` — [FastMCP docs](https://gofastmcp.com/deployment/http). Its docs claim more than a million downloads a day and that it powers about 70% of MCP servers — [FastMCP](https://gofastmcp.com/getting-started/welcome). That is a self-reported claim.
- **TypeScript and Cloudflare:** `@modelcontextprotocol/sdk` 1.32.2 was the npm `latest` on 2026-10-23, and `agents` 0.32.0 on 2026-10-29 ([npm](https://www.npmjs.com/package/agents)). Cloudflare's templates use a stateless `createMcpHandler`, `McpAgent` is deprecated, and there is a `remote-mcp-authless` template — [Cloudflare](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)
- **Datasette:** `datasette-mcp` 0.3 adds a `/-/mcp` server to any Datasette instance and requires `mcp>=2.1.1` — [PyPI](https://pypi.org/project/datasette-mcp/)
- **Local measurement, SDK spike on 2 Nov 2026** (`mcp` 2.3.0, stateless, real `plans_dataset.json`):
  - 28 packages installed (including `cryptography`, `pydantic_core`, `PyJWT`, `uvicorn`), 54 MB venv with `snowballstemmer` and pip included.
  - About 1.0 s startup, 81 to 89 MB resident memory, tool call p50 7.5 ms and p95 14.9 ms on localhost.
  - Modern `server/discover` and `tools/call`, legacy `initialize` (2025-06-18), and legacy `tools/call` with no session all succeeded.
  - Header mismatch returned `-32020`, a bad Origin 403, a bad Host 421, DELETE 405.
- **Three spike findings the docs did not warn me about:**
  - **GET to `/mcp` returned 200 and held the connection open** (cut off by my 3 s client timeout). This is the legacy stream, and on a public endpoint it is a cheap way to tie up connections.
  - `tools/list` and `server/discover` default to `ttlMs: 0, cacheScope: private`, so the new caching does nothing unless configured.
  - `server/discover` advertised `listChanged: true` and `subscribe: true` by default.

### Inferences
- **Why not FastMCP:** for five tools the official SDK is enough. FastMCP's extras (proxying, code mode, auth providers) go unused, and it adds a second release stream to track.
- **Why not TypeScript:** it would duplicate the query logic in a second language, in a repository whose whole toolchain is Python. It only makes sense if Cloudflare Workers is chosen for other reasons.
- **Suggested layout** (the repository has no `pyproject.toml` today):
  - `lautakuntamuistiot/query.py`: stdlib only, Python 3.8+ compatible, covering load, filter, FTS5, haversine and provenance. Tested with `unittest`.
  - `mcp_server/server.py`: the only file that imports `mcp`. It maps tools to `query.py`.
  - `mcp_server/requirements.txt`: a hash-locked file (`--require-hashes`), plus `mcp_server/Dockerfile`.
  - A CI check that fails if anything under `lautakuntamuistiot/` imports a non-stdlib module, so the rule is enforced rather than hoped for.
  - A `[project.optional-dependencies] mcp = [...]` extra is the more conventional shape, but it means adding packaging to a project that deliberately has none. A separate directory is simpler, and the README line "nothing to `pip install`" stays true for the scrapers.
- **Stdlib-only server as a fallback:** because 2026-07-28 is plain POST and JSON, a server on `http.server` plus `sqlite3` is now conceivable: discover, list, call, plus a stateless legacy `initialize`, behind a reverse proxy. It would remove all 28 packages. I do not recommend it first, because header validation, two protocol eras and future revisions become hand-maintained. It is worth keeping in mind if supply-chain review of the SDK becomes a concern, and the conformance suite could check it.

### Gaps
- I did not verify that the TypeScript `latest` 1.32.2 implements the modern era, or whether a separate v2 package exists.
- I did not verify that the `mcp` SDK runs on Python Workers.
- I did not find the SDK setting that raises `ttlMs` and `cacheScope`, or how to disable the GET stream. Both need a look at the SDK source, or a small ASGI middleware that answers GET with 405.

## Which hosting option fits, at what cost, and where can data stay in the EU?

### Takeaway
Hosting is cheap on all serious options. **Cloud Run in `europe-north1` (Finland)** is likely free at this traffic and needs no server maintenance. **A Hetzner server in Helsinki at EUR 5.99/month** is the alternative when a fixed bill and an EU-owned provider matter more than avoiding server upkeep. Since the endpoint is anonymous, worst-case cost matters more than typical cost.

### Cited Findings

| Option | Price seen 2026-11-02 | EU location | Fit |
|---|---|---|---|
| **Google Cloud Run** | Free per month: 180,000 vCPU-s, 360,000 GiB-s, 2 M requests (request billing). Then $0.000024/vCPU-s and $0.0000025/GiB-s active, $0.40 per million requests. Idle with min instance: $0.0000025 for each — [Cloud Run pricing](https://docs.cloud.google.com/run/pricing) | `europe-north1` (Finland) and `europe-north2` (Stockholm), both Tier 1 — [same page](https://docs.cloud.google.com/run/pricing) | Scale to zero, managed TLS, cold starts |
| **Azure Container Apps** | Free per month: 180,000 vCPU-s, 360,000 GiB-s, 2 M requests — [Azure pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/). Sweden Central: $0.000024/vCPU-s active, $0.000003/GiB-s, $0.40 per million — [Azure Retail Prices API](https://prices.azure.com/api/retail/prices) | Sweden Central, North Europe, West Europe and others | Same model as Cloud Run, and scales to zero |
| **Fly.io** | No free tier for new organizations. shared-cpu-1x: 256 MB $2.19, 512 MB $3.69 in the cheapest regions. Frankfurt 1 GB $7.73. Stopped machines $0.15/GB/month. Shared IPv4 free. Europe egress $0.02/GB — [Fly pricing](https://docs.fly.io/about/pricing) | Stockholm `arn`, Amsterdam, Paris, Frankfurt — [Fly regions](https://docs.fly.io/reference/regions/) | Simple containers, a few dollars a month |
| **Hetzner Cloud** | CX23 (2 vCPU, 4 GB, 40 GB) EUR 5.99/month, CAX11 (2 Arm, 4 GB) EUR 6.49, CPX02 (1 AMD, 1 GB) EUR 6.49, excl. VAT, with IPv4 and 20 TB traffic in EU included, and a monthly price cap — [Cost-Optimized](https://www.hetzner.com/cloud/cost-optimized/), [Regular Performance](https://www.hetzner.com/cloud/regular-performance/) | Helsinki, Falkenstein, Nuremberg. The static page showed some models as "not available", so check the console for Helsinki stock | Fixed bill, you patch the OS |
| **Cloudflare Workers** | Free: 100,000 requests/day, 10 ms CPU per invocation. Paid: $5/month minimum, with 10 M requests and 30 M CPU-ms included. D1 free: 5 M rows read/day, 5 GB — [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/). Startup limit 1 s, size limit 64 MiB — [Limits](https://developers.cloudflare.com/workers/platform/limits/) | D1 has location hints (`weur`, `eeur`) and jurisdiction restriction — [D1 location](https://developers.cloudflare.com/d1/configuration/data-location/). D1 includes FTS5 — [D1 SQL](https://developers.cloudflare.com/d1/sql-api/sql-statements/) | Cheapest at scale, but a TypeScript rewrite |
| **Hugging Face Spaces** | CPU Basic hardware has no hourly cost, but Docker and Gradio Spaces now **require a paid plan** to create. Free hardware sleeps when unused and disk is not persistent — [Spaces overview](https://huggingface.co/docs/hub/spaces-overview) | Compute region not stated on the [pricing page](https://huggingface.co/pricing) | Poor fit |

- **Local calculation for Cloud Run:** 100,000 calls a month at the 100 ms billing minimum, 1 vCPU and 512 MiB, is 10,000 vCPU-s and 5,000 GiB-s, about 6% and 1.4% of the free grant. Even 1 million calls stays inside it (100,000 vCPU-s). Expected bill: $0, excluding a domain name. Rates are from the [pricing page](https://docs.cloud.google.com/run/pricing).
- **Local calculation, worst case with `--max-instances=1`:** if an abuser kept one instance busy all month, 2,592,000 s × ($0.000024 + 0.5 × $0.0000025) comes to about $65, plus about $0.40 per million requests. Without a cap, cost grows with instance count.
- **Local calculation, a warm instance:** one always-on instance at 1 vCPU and 512 MiB at idle rates costs about $9.70/month. I did not confirm how the free grant applies to idle time.

### Inferences
- **Ranking for this project:**
  1. **Cloud Run `europe-north1`**: no patching, TLS included, Finnish region, likely $0. Set `--max-instances=1`, `--concurrency` around 40, and a budget alert (alerts notify, they do not cap). One instance is plenty given 7.5 ms tool calls.
  2. **Hetzner CX23 in Helsinki**: the only option with a hard monthly bill cap and a European owner. Costs maintainer time: Caddy for TLS, `unattended-upgrades`, a systemd service. Choose it if a city partner asks about EU sovereignty or if denial-of-wallet worries you more than patching does.
  3. **Fly.io `arn`**: a sensible middle at about $3 to $5/month with no idle-free tier.
  4. **Cloudflare Workers**: only if the team accepts TypeScript. The Free plan's 10 ms CPU limit looks too tight to parse a 3.2 MB dataset per isolate, so D1 or the paid plan would be needed.
  5. **Azure**: equivalent to Cloud Run. Choose it only if there is already an Azure relationship.
  6. **Hugging Face**: not suitable for a public service.
- **Data location is a modest concern here.** The dataset is public and the only personal data at risk is in request logs (see security). Hosted clients call from their own cloud anyway, so the user's query reaches a US AI vendor regardless of where this server sits. EU hosting mostly reduces what this project itself handles and looks right for a Finnish civic service.
- A cold start of a few seconds is acceptable because of Claude's 240 s tool limit, but test connector setup under a cold start, since Claude's 10-second limits on OAuth endpoints show that vendors do set short timeouts on some paths. I found no stated connect timeout for authless servers.

### Gaps
- Fly's per-region price table loads dynamically, so `arn` prices for 256 MB and 512 MB are not confirmed.
- Hugging Face PRO price was not on the page read.
- I did not verify Cloudflare's Worker compute EU restriction (Regional Services), so assume compute runs globally.
- Cloud Run cold-start time was not measured on Google's hardware. The spike's 1.0 s startup was on a laptop.

## Which data backend suits this volume, how should Finnish search work, and how should updates reach the server?

### Takeaway
At this size **no database server or prebuilt artifact is needed**: load JSON at startup and build an **in-memory SQLite FTS5** index from the stdlib in tens of milliseconds. No tokenizer solves Finnish alone, so combine a place-name gazetteer, prefix or stem matching, and letting the calling model retry. Skip vector search until evals show a need.

### Cited Findings
- **Actual volume (local measurement, [`data/`](../../../data/)):** `plans_dataset.json` is 3.2 MB and `kerrokantasi_dataset.json` 348 KB. There are 1,727 located decisions, 105 unlocated and 185 consultations, 2,017 records in total, about 3.2 M characters as JSON. Median record 1,115 bytes, p95 3,158, maximum 10,788 (driven by `attachments`). 833 of 2,017 records (41%) have no `summary`.
- **Local measurement, load and search:** JSON load 15 ms. FTS5 index build 15 ms (unicode61) and 40 ms (trigram). FTS5 query with `bm25` and `snippet` about 0.17 ms. Plain Python substring scan over all records about 4.8 ms. Full haversine sort over 1,912 points about 2.1 ms.
- **FTS5 tokenizers:** unicode61 (default), ascii, porter ("for use with English language terms only") and trigram. Trigram needs at least 3 characters to match. Prefix queries use `word*`, and `prefix=` options build prefix indexes. `snippet()` returns up to 64 tokens. `bm25()` accepts column weights. Custom tokenizers require the C API. The page mentions no Finnish stemmer — [SQLite FTS5](https://www.sqlite.org/fts5.html)
- **Diacritics:** `remove_diacritics` defaults to 1 in unicode61 — [SQLite FTS5](https://www.sqlite.org/fts5.html). I tested with 0 to keep ä and ö distinct.
- **Snowball Finnish:** a six-step suffix stripper. "Normalising strong and weak forms after ending removal is not generally possible", with only single/double final consonants handled. Compounds are not discussed — [Snowball](https://snowballstem.org/algorithms/finnish/stemmer.html). `snowballstemmer` 3.1.1 is on [PyPI](https://pypi.org/project/snowballstemmer/).
- **Finnish difficulty:** single words may take thousands of forms across up to 15 cases — [Finnish ModernBERTs paper](https://arxiv.org/html/2511.09213v1)
- **Voikko:** morphological analysis giving a `BASEFORM` lemma via `libvoikko.Voikko("fi").analyze()` — [Solita tutorial](https://data.solita.fi/?p=277). The PyPI wrapper `libvoikko` is 4.3 from 2019-11-22 ([PyPI](https://pypi.org/project/libvoikko/)), and needs the native library plus `voikko-fi` data ([corevoikko](https://github.com/voikko/corevoikko)).
- **Local measurement, match counts on real data (2,017 records):**

| Query | unicode61 exact | Prefix (`Jätkäsa*` style) | Trigram | Snowball stem |
|---|---|---|---|---|
| Jätkäsaari / Jätkäsaaressa | 51 / **0** | 60 | 51 / 0 | 58 / 58 |
| Herttoniemi / Herttoniemessä | 49 / 3 | 63 | 49 / 3 | 58 / 58 |
| Malmi / Malmin | 66 / 41 | 91 | 91 / 59 | 76 / 76 |
| Viikki / Viikin | 16 / 6 | 24 | 17 / 14 | 17 / 17 |
| katu / kadun | 82 / 10 | 520 | **706** / 124 | 81 / **32** |
| kaava / kaavan | 4 / 4 | 51 | **1,075** / 882 | 6 / 6 |
| pyörätie / pyöräteiden | 5 / 1 | 31 | 7 / 1 | 6 / 3 |

- **Scope of that table:** the Snowball column covers 1,912 records (located decisions and consultations, without the 105 unlocated). The other columns cover all 2,017, so compare the Snowball column with them only roughly. Prefix uses a stem trimmed by up to 3 letters with a 4-letter minimum, for example `katu*`, `kaav*`, `pyörä*`.
- **Local measurement, Snowball pair agreement:** it conflated 15 of 21 test pairs. It handled place names well (Jätkäsaari, Hakaniemi, Vuosaari, Viikki). It missed gradation and irregular forms (katu/kadun, Lahti/Lahden, Kruununhaka/Kruununhaan, tie/teiden, pyörätie/pyöräteiden, raitiotie/raitiotien). Stemming and indexing all records took 1.2 s in pure Python.
- **Repository assets for query normalisation:** `data/geocode_cache.json` has 1,220 looked-up names, and the records have 879 distinct `location` values. `locate.py` already restores inflected names to nominative (*Caloniuksenkadun* to *Caloniuksenkatu*, *Viikin* to *Viikki*) — [README](../../../README.md)
- **Embeddings:** mE5 reports MIRACL only as a 16-language average, 65.7 for large-instruct, with a 512-token context — [Multilingual E5 report](https://arxiv.org/pdf/2402.05672). I found no Finnish-specific figure. Community Finnish trims of mE5 exist without benchmarks ([example](https://huggingface.co/alphaedge-ai/multilingual-e5-small-fin-32768)). `sqlite-vec` is at 0.1.9, still pre-1.0 ([PyPI](https://pypi.org/project/sqlite-vec/)).
- **Other engines:** DuckDB 2.0.0 ([PyPI](https://pypi.org/project/duckdb/)) and Datasette 0.65.5 ([PyPI](https://pypi.org/project/datasette/)) are available. SpatiaLite was not evaluated, and R*Tree is compiled into the local SQLite (local measurement).
- **Update path trap:** events triggered by `GITHUB_TOKEN` "will not create a new workflow run", except `workflow_dispatch` and `repository_dispatch` — [GitHub docs](https://docs.github.com/en/actions/concepts/security/github_token). The daily job commits with that token ([`update-data.yml`](../../../.github/workflows/update-data.yml)), so **a deploy workflow `on: push` to `data/` would never fire**.
- **Other update facts:** GitHub caches raw files for about 5 minutes — [README](../../../README.md). Most days the job stops after the check, since it commits only on change — [`update-data.yml`](../../../.github/workflows/update-data.yml).

### Inferences
- **Search design, in order:**
  1. **Gazetteer step.** Normalise the query against known places using the `location` values, Kerro kantasi `labels` and `locate.py`'s base-form logic. A hit becomes a strong `location` boost.
  2. **FTS5 on `heading`, `title`, `summary`, `location`**, with `unicode61 remove_diacritics 0`, weighting `location` and `heading` highest, and querying a trimmed prefix.
  3. **A plain-language hint on empty results**, naming the base form to try. The caller is an LLM and can usually expand *kadun* to *katu* or try synonyms if told to. This is why a weak stemmer is tolerable here.
- **Avoid trigram as the default.** It gives real substring recall but massively over-matches common Finnish compound heads: `kaava` hits 1,075 of 2,017 records through *asemakaava*, and `katu` hits 706 through every *-katu* street. It is useful as a fallback for a rare street fragment only.
- **Snowball is an optional later addition**, not v1. It is pure Python and could run at build time, but adds a dependency and takes about 1.2 s of startup for moderate gain over gazetteer plus prefix. If evals show lexical misses, add Voikko **at build time in the Action only**, writing a lemma column into a generated file, so no native library reaches the server. The 2019 wrapper date is a reason to test before committing.
- **DuckDB, SpatiaLite and geohash are unnecessary.** Haversine in Python at 2 ms is fast enough, and there are under 2,000 points.
- **Spatial results need honest precision.** `geocode` is `street` for 1,188 records, `district` 442, `area` 165, `place` 111. A pin is a point on a street or a district centre, not the plan's extent, per the [README](../../../README.md). Radius search must return `location_precision` and should rank `district` hits below `street` hits.
- **Vector search is not justified for v1.** Text is short and place-name heavy, 41% of records lack a summary, and the Finnish evidence is thin. A local model would add gigabytes and long cold starts, and a hosted embedding API would send user queries to another party (my inference, not measured). Add it only if evals show semantic misses, for example *pyöräily* against *pyörätie*.
- **Datasette is a reasonable data browser but the wrong primary interface.** It would expose a schema rather than task-shaped tools, and the caveats (`stage` semantics, approximate location) would be left to the model. I did not inspect which tools `datasette-mcp` exposes.
- **Recommended update path:**
  - **Cloud Run:** add a `deploy-mcp` workflow triggered by `workflow_run` on "Update data" (or `gh workflow run` from the job, since it already has `actions: write`), that builds an image containing `data/` and deploys with Google OIDC. An immutable image gives a clean `data_version` equal to the git SHA.
  - **Hetzner:** a systemd timer on the server runs `git pull --ff-only` and swaps the in-memory index atomically. This pull model means GitHub holds no deployment credentials.
  - **Either way, add a validation gate:** refuse to go live if record count falls more than a few percent or the schema check fails.
- **Scope decision needed:** the zoning archive (4,413 plans, polygons) described in the README is **not in `data/`**, as `asemakaava_dataset.json` is absent. Including it needs a publishing step and changes data volume substantially.

### Gaps
- Voikko's licence and its compound-word output were not confirmed from what I read, and I did not run it.
- No published Finnish lemmatized BM25 versus dense retrieval comparison was found.
- The counts table shows volume, not relevance. Precision and recall need labelled queries (see testing).
- FTS5 presence in the chosen container's Python build should be asserted at startup. I only checked the local builds.

## How should the tools be designed, and what is a proposed tool, resource and prompt set for this repository?

### Takeaway
Ship **about five task-shaped read-only tools**, not a wrapper around the JSON or a raw SQL tool. Each result must carry its source link, decision stage and location precision, because the dataset's main risk is a model reporting a heuristic guess as a city decision.

### Cited Findings
- **Anthropic, "Writing effective tools for AI agents" (11 Sep 2025):**
  - More tools do not necessarily give better results, so build a few for high-impact workflows and avoid overlap.
  - Return high-signal fields and resolve cryptic IDs to names. A `response_format` enum gave 72 versus 206 tokens in its example.
  - Use pagination, filtering and truncation with sensible defaults, and make errors actionable.
  - Namespacing choice has measurable effects and varies by model, so test it — [Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)
- **Block's playbook (16 Jun 2025, over 60 MCP servers):**
  - Design "top-down from workflows, not bottom-up from API endpoints".
  - Tool names and descriptions are effectively prompts.
  - LLMs still struggle to chain many calls.
  - Guard against oversized output with an actionable error.
  - Avoid dynamic data such as timestamps in instructions because it breaks prompt caching.
  - Keep each tool to one risk level.
  - The article gives no quantitative benchmarks — [Block](https://engineering.block.xyz/blog/blocks-playbook-for-designing-mcp-servers)
- **GitHub Copilot (19 Nov 2025):** trimming about 40 built-in VS Code tools to 13 core tools cut average latency by 400 ms. Tool coverage was 94.5% with embedding selection, 87.5% with LLM selection and 69.0% with the static default. Benchmarks gained 2 to 5 percentage points — [GitHub Blog](https://github.blog/ai-and-ml/github-copilot/how-were-making-github-copilot-smarter-with-fewer-tools/). This measures Copilot's own tools in a coding setting, so it is only analogous.
- **Secondary report:** GitHub cut agent workflow tokens by up to 62%, with unused tool registrations costing 8 to 12 KB of context per call — [i-programmer](https://www.i-programmer.info/news/90-tools/18913-github-cuts-token-use-to-reduce-bills.html). I did not read the original post.
- **Size limits to design around:** about 150,000 characters on Claude's hosted surfaces ([Claude](https://claude.com/docs/connectors/building/index.md)), 25,000 tokens and a warning at 10,000 in Claude Code ([Claude Code](https://code.claude.com/docs/en/mcp)).
- **Local measurement, payload size:** 10 records take about 4,500 characters with a concise field set and 10,400 with all fields. The whole corpus is 3.2 M characters, far over any limit. Token figures would be rough, since Finnish tokenizes poorly, and I did not measure them with a real tokenizer.
- **Local measurement, identifier problem:** `dm + asia_id + plan_type`, the README's upsert key, has 2 duplicates across the 2,017 records. `asia_id` alone has 75 and `asia_id + plan_type` has 22. `decision_url` is unique for all 2,017.
- **Field traps in the data:**
  - The dataset's `map_url` is the **plan drawing PDF**, not a map. `build_umap` already calls it `drawing_url` — [README](../../../README.md)
  - `date` is `DD.MM.YYYY` — [`data/`](../../../data/)
  - Zoning `proposal` records are not approvals, which the README calls out, and `stage` is a keyword heuristic — [README](../../../README.md)
  - The 100-record quality sample is unreviewed, so accuracy is unmeasured — [README](../../../README.md)
- **Attribution duties:** coordinates are ODbL via OpenStreetMap, Kerro kantasi data is ODbL, and decisions are non-copyright under section 9 of the Copyright Act — [README](../../../README.md)
- **Prompt and resource reach:** Copilot documents prompts and resources only for VS Code ([GitHub](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/extend-copilot-chat-with-mcp)), so nothing essential may live only there.
- **Location data rule:** OpenAI's guidelines forbid requesting precise location and suggest coarse location from the client — [OpenAI](https://developers.openai.com/apps-sdk/app-submission-guidelines)

### Inferences

**Proposed tools** (all `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: false` for a bounded dataset, each with a `title` and `additionalProperties: false`):

| Tool | Purpose | Key parameters |
|---|---|---|
| `search_plans` | Find decisions and consultations by words and place | `query`, `plan_types[]` (katu, liikenne, puisto, asemakaava, muu_k, kerrokantasi), `stages[]` (approved, proposal, returned, other, consultation), `year_from`, `year_to`, `include_unlocated=false`, `limit=10` (max 50), `cursor`, `detail=concise` |
| `get_plan` | One record in full, including attachments and drawings | `id` |
| `find_plans_near` | Plans around a named place | `place` (name from the gazetteer), or optionally `lat` and `lon`, `radius_m=500`, filters, `limit`, `cursor` |
| `list_open_consultations` | Kerro kantasi hearings still open, soonest close first | `limit`, `cursor` |
| `summarize_plans` | Counts by `year`, `stage`, `plan_type` or `location`, for trend questions without fetching records | `group_by`, the same filters |

Design notes:
- **The time-sensitive tool earns its place.** "Can I still comment?" is a high-value citizen question, and one hearing (*Vastaa Pitäjänmäen karttakyselyyn!*) was open on 2 Nov 2026 by my check of `close_date`. Note that Kerro kantasi's `generated` date was 2026-10-20 while plans were 2026-11-01, so the open list can lag if hearings were not rewritten. Compute openness from `close_date` at request time.
- **No raw SQL tool.** Block's Linear example argues for generic query tools in some cases, but the audience here is non-technical users and a model that must honour `stage` semantics. Claude's checklist also adds documentation requirements for custom query tools.
- **Stable IDs:** derive `id` from `decision_url` (for example a short hash, or `asia_id` plus the `paatos` value). Do not use the README's upsert key, which collides. Check the two colliding records, since that may be a data bug worth fixing separately.
- **Output field mapping:** rename `map_url` to `drawing_url`, `decision_url` to `source_url`, `geocode` to `location_precision`, and `date` to ISO `decision_date`. Hide `lat` and `lon` in concise mode unless the tool is spatial. Never expose `seen_decisions` or `fetch_failures`, and leave out low-value codes such as `dm`.
- **Concise result shape:** `id`, `title`, `decision_date`, `plan_type`, `stage`, `location`, `location_precision`, `source_url`, `drawing_url`, and a `summary` that may be `null`.
- **Envelope for provenance, once per response, so it does not repeat per record:**
  ```json
  {"results": [], "total": 51, "next_cursor": null,
   "provenance": {"data_version": "<git sha>", "data_as_of": "2026-11-01",
     "source": "Automatically extracted from public City of Helsinki documents; not an official dataset. Verify against source_url.",
     "stage_note": "stage is a keyword heuristic. A zoning 'proposal' is not an approved plan.",
     "location_note": "Approximate. See location_precision.",
     "attribution": "Decisions: City of Helsinki. Consultations: Kerro kantasi (ODbL). Coordinates: OpenStreetMap contributors (ODbL)."}}
  ```
  Return it as `structuredContent` with an `outputSchema`, plus the same JSON in a text block as the spec suggests. Test a compact readable text form against it in evals, since Anthropic reports format can affect results.
- **Keep the `data_as_of` date out of tool descriptions and server instructions** (Block's prompt-caching point), and keep it in results only.
- **Limits:** default 10, maximum 50, so a maximum page stays near 22,000 characters and under Claude Code's warning. `attachments` and `drawings` only appear in `get_plan`, because one record can reach 10.8 KB. Use an opaque cursor encoding the offset and `data_version`, and on a stale cursor return an `isError` telling the model to restart.
- **Errors in the model's terms:** for example, *"No results for 'Jätkäsaaressa' with stage=approved, year_from=2025. Without the stage filter there are 12. Known place: Jätkäsaari."* Unknown `plan_types` values should list valid ones.
- **Language:** data is Finnish and tool descriptions should be English with Finnish terms and examples, since that gives models the mapping *katusuunnitelma = street plan*. Verify with Finnish and English eval prompts. Do not translate records on the server.
- **Naming:** use a short server name without underscores, such as `helsinkiplans`, because of Gemini's `mcp_{server}_{tool}` rule and 63-character limit. Tool names stay well under Claude's 64.
- **ChatGPT compatibility, phase 2:** expose `search` and `fetch` with OpenAI's exact shape on a **separate path** such as `/mcp/chatgpt`. `search` takes only one string, so it cannot replace `search_plans`, and putting both on one endpoint would create overlapping tools. Separate endpoints avoid this without breaking the rule that `tools/list` must not vary per connection.
- **Set `ttlMs` high (about 1 hour, or longer for tool lists) with `cacheScope: public`**, since the data changes at most daily.

**Proposed resources** (a convenience only, duplicated by tools where essential):
- `helsinkiplans://about`: coverage, caveats, field meanings and licences.
- `helsinkiplans://plan/{id}`: a resource template for one record.
- Do not serve the dataset as a resource. Point to the raw GitHub files and the uMap map for bulk use.

**Proposed prompts** (user-invoked, Finnish and English):
- `place_briefing(place)`: what has been decided and proposed at this place, by stage, with source links.
- `open_consultations_digest`: what can be commented on now, and how to do it.
- `explain_plan_stage(id)`: what this stage means and who decides next.

**MCP Apps:** a later option. A `ui://` map view would suit this data, but first return a link to the existing uMap map. Client support varies and every App needs a working text fallback.

**Elicitation:** not needed. Return candidates when a place is ambiguous and let the model ask.

### Gaps
- No controlled published evidence was found on the best tool count for a small civic data server. The numbers above are analogies.
- Whether English or Finnish tool descriptions select better is untested, so it belongs in evals.
- How hosted clients render `resource_link` versus plain URLs, and whether they produce citations other than in ChatGPT, was not tested.

## What does security look like for a public read-only server?

### Takeaway
With no secrets, no writes and no user accounts, the worst outcomes are poisoned text reaching someone's assistant, service abuse and a compromised dependency or deploy credential. Treat scraped text as hostile data. Per-IP rate limiting alone will not work, because Claude's traffic arrives from a single shared range.

### Cited Findings
- **OWASP MCP Top 10** (beta, marked 2025): items include MCP03 Tool Poisoning, MCP04 Supply Chain, MCP06 Prompt Injection via Contextual Payloads, MCP08 Lack of Audit and Telemetry and MCP10 Context Injection and Over-Sharing — [OWASP](https://owasp.org/www-project-mcp-top-10/)
- **OWASP MCP Security Cheat Sheet:**
  - Sanitize outputs, but tag stripping and pattern detection "cannot establish that the remaining text is safe".
  - Return only the structured data needed, not raw HTML.
  - Pin reviewed tool definitions with hashes, including schemas and annotations.
  - Use rate limits, quotas and timeouts.
  - "Never fetch arbitrary URLs provided by the LLM without strict allowlist validation."
  - Validate `Origin` on Streamable HTTP and the Host header on all requests — [OWASP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html)
- **OpenAI on prompt injection:** trusting the developer doesn't make the server safe if its content could include untrusted input — [OpenAI](https://developers.openai.com/api/docs/mcp/)
- **Spec, DNS rebinding:** servers MUST validate `Origin` on all connections and return 403 if it is present and invalid. Local servers SHOULD bind to localhost. Servers SHOULD implement authentication for all connections — [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
- **Anthropic's review rejects tool descriptions** that instruct Claude to call unrequested software, pull behavioural instructions from elsewhere or contain hidden instructions — [review criteria](https://claude.com/docs/connectors/building/review-criteria)
- **SDK behaviour:** DNS rebinding protection is automatic only when `host` is localhost. Serving a real hostname needs `TransportSecuritySettings(allowed_hosts=[...], allowed_origins=[...])` — [Migration guide](https://py.sdk.modelcontextprotocol.io/migration/). `max_request_body_size` defaults to 4,194,304 bytes (local inspection of the 2.3.0 signature).
- **Rate-limit trap:** Anthropic's traffic originates from `160.79.104.0/21` — [Claude auth docs](https://claude.com/docs/connectors/building/authentication). Claude's troubleshooting lists WAF 403 and 429 responses as a connection-failure cause — [Troubleshooting](https://claude.com/docs/connectors/building/troubleshooting.md)
- **Incidents (secondary sources, primary reports not read):**
  - `mcp-remote` CVE-2025-6514, a command injection through a crafted authorization URL, rated CVSS 9.6.
  - The malicious `postmark-mcp` npm package, clean through 1.0.15 and backdoored in 1.0.16 — [Docker](https://www.docker.com/blog/mcp-horror-stories-the-supply-chain-attack/), [Zealynx](https://www.zealynx.io/research/adversarial-security/mcp-breach-index-2025-2026)
- **Local measurement:** a crude pattern scan of `summary` fields (`ignore`, `system prompt`, `<script`, URLs) found 0 hits. As OWASP says, this cannot establish safety.
- **Ingested text is limited:** decision `summary` is capped at 320 characters in code ([`common.py`](../../../lautakuntamuistiot/common.py)). Kerro kantasi summaries reached 536 characters at most (local measurement), and no public comments are collected ([README](../../../README.md)).

### Inferences

**Threat model for this repository:**
- **Result poisoning.** Text comes from city-authored pages, so likelihood is low but not nil: pages can be compromised, and attachment names and hearing text are lightly controlled. Impact depends on the *client's other tools*: a read-only server can still carry an instruction into a session that has email or file connectors.
  - Keep responses structured, and strip control characters, zero-width characters and HTML from all text fields at load time.
  - Keep the field length caps, and apply them to `heading`, `title` and attachment labels too.
  - Validate every output URL against a host allowlist built from the data: `paatokset.hel.fi`, `ahjojulkaisu.hel.fi`, `www.hel.fi`/`hel.fi`, `kerrokantasi.hel.fi`, `kerrokantasi.api.hel.fi`, `ptp.hel.fi`. Drop anything else. Confirm the list against the data before enforcing it.
  - Add no text to results that addresses the model as instructions, beyond neutral field notes.
- **SSRF.** Provide no tool that fetches a model-supplied URL. If PDF reading is added later, accept only a record `id`, fetch server-side from allowlisted hosts with size and time limits, and treat that text as far riskier than the current short fields. It would also change the copyright position, since drawings are deliberately "linked, not copied".
- **Abuse and cost:**
  - Cap instances (see hosting).
  - Set `max_request_body_size` to about 64 KB, cap `query` at about 200 characters and `limit` at 50, and apply request timeouts of a few seconds.
  - Quote user terms before passing them to FTS5 `MATCH`, both to prevent query-syntax errors and to stop expensive constructions.
  - **Close GET on `/mcp`** with a 405 (the spike showed it held connections open). The 2026-07-28 page tells modern-only servers to answer GET this way, so test that legacy clients still work with it.
  - Use a global concurrency limit as the primary control, with a *generous* per-IP limit as a backstop. Never send 429s based on a low per-IP rate, or all Claude users share one bucket and the connector appears broken.
  - `clientInfo` is self-declared, so do not trust it for limits.
- **DNS rebinding and Origin.** This mostly protects local servers. For a public server, set `allowed_hosts` to the public hostname. Allow absent `Origin` (server-side clients do not send one), and allow a short list of browser origins. Decide explicitly whether browser-based clients are wanted, since the allowlist will otherwise reject them with 403.
- **No authentication.** The spec's SHOULD on authentication is outweighed here by the goal of open public data, and Claude's checklist explicitly accepts it. Adding OAuth would bring an authorization server, token handling and attack surface for no benefit. API keys are worth adding only if abuse appears.
- **Supply chain and CI:**
  - Lock with hashes (`--require-hashes`) and enable automated dependency alerts.
  - Keep the Docker base image pinned by digest, and run as non-root on a read-only filesystem.
  - Pin third-party Actions by SHA in any new workflow. `update-data.yml` uses tags (`@v7`).
  - **Do not add deploy credentials to the scraping job.** It holds `contents: write` and processes untrusted web pages. Deploy from a separate workflow using short-lived OIDC credentials, with only what it needs.
  - Hash tool definitions in a test so any change to names, descriptions, schemas or annotations is a deliberate reviewed diff, per OWASP.
  - SDK upgrades deserve review: the SDK v2 rename and the stateless protocol change both landed in 2026.
- **Conflict to resolve:** OWASP says to "log all MCP tool invocations with full parameters, user context, and timestamps", which is enterprise guidance. On an anonymous public service, full query logging would create a personal-data store: people may search for their home street. Minimal logging (see next section) is the better fit here, and the deviation should be documented.
- **Reputational risk is probably the largest in practice:** a model stating "the committee approved X" when `stage` is a guess. It is not a classical security issue, but provenance in every response is its main mitigation, and evals should test it.

### Gaps
- I found no published incident of tool-result poisoning through a civic or public-records MCP server.
- Primary sources for the CVE and `postmark-mcp` cases were not read. Figures above come from secondary writeups.
- Finnish and EU legal treatment of request logs was not researched here, and needs review by whoever handles the privacy policy.

## How do people test and evaluate MCP servers, and how can usage be measured without invading privacy?

### Takeaway
Layer three checks: protocol conformance in CI (Inspector CLI and the conformance suite), deterministic unit tests of the stdlib query core, and an agent eval set of realistic Finnish and English tasks measuring accuracy and tool selection. For usage, count aggregates such as tool name, status, duration and result count, and do not store query text or full IPs.

### Cited Findings
- **MCP Inspector:** v2.13.0 on npm (2026-10-28) requires Node 22.19.0 or newer and has web, CLI and TUI clients, with modern and legacy era handling. CLI example: `npx @modelcontextprotocol/inspector --cli https://api.example.com/mcp --transport http --method tools/call --tool-name get_weather --tool-arg city=Boston --format json` — [Inspector](https://modelcontextprotocol.io/docs/tools/inspector)
- **Conformance suite:** the official repository `modelcontextprotocol/conformance` ("Conformance Tests for MCP") was active on 2026-10-26 — [GitHub](https://github.com/modelcontextprotocol/conformance). I did not read its usage docs.
- **Eval method (Anthropic):**
  - Generate dozens of realistic tasks with verifiable outcomes, using exact-match or LLM-judge verifiers.
  - Run them in a simple agent loop and optionally specify expected tools, without overspecifying.
  - Collect accuracy, runtime per tool call and task, total tool calls, tokens and tool errors.
  - Keep a held-out test set.
  - Many redundant calls suggest pagination problems. Many invalid-parameter errors suggest description problems — [Anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)
- **Directory expectation:** run every tool through Inspector and as a custom connector in Claude before submitting — [review criteria](https://claude.com/docs/connectors/building/review-criteria)
- **Telemetry standards:** the spec replaces the Logging feature with OpenTelemetry guidance ([Deprecated features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)) and documents trace context `_meta` keys ([Changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog)).
- **OpenTelemetry attributes (secondary, Development stability):** `mcp.method.name`, `gen_ai.tool.name`, `error.type` — [Last9](https://last9.io/blog/mcp-server-monitoring/), [Elastic](https://www.elastic.co/observability-labs/blog/mcp-tracing-opentelemetry-elastic-apm)
- **Vendor metrics:** Anthropic's portal provides server health and usage metrics after publication — [Submission](https://claude.com/docs/connectors/building/submission)
- **OpenAI data minimisation:** collect only what each tool needs, with no "just in case" fields — [OpenAI](https://developers.openai.com/apps-sdk/app-submission-guidelines)

### Inferences

**Test layers for this repository:**
1. **Query core (`unittest`, stdlib, runs with the existing toolchain):** inflected place lookups using the table above as regression cases, filters, pagination, cursor staleness, FTS5 quoting of hostile input (`"`, `*`, `NEAR(`, very long strings), and the URL allowlist.
2. **Contract snapshot:** a hash of the `tools/list` output, plus deterministic ordering.
3. **Protocol, in CI against a running container:** Inspector CLI for `tools/list` and one call of each tool, the conformance suite, and `curl` checks for both eras, Origin 403, Host 421, header mismatch `-32020`, and GET 405.
4. **Agent evals (40 to 60 tasks, half Finnish, 25% held out):** run against at least Claude and one GPT model, and ideally Gemini, since Gemini strips some schema fields. Ground truth is computed from the dataset with `id` sets. Example categories:
   - Lookup: "Mitä katusuunnitelmia on hyväksytty Jätkäsaaressa vuonna 2025?" (uses an inflected place; exact `id` set).
   - Stage honesty: "Onko [zoning plan with stage=proposal] hyväksytty?" The answer must not claim approval, and must point to the City Board/Council step.
   - Time: "Mihin Kerro kantasi -kyselyyn voin vielä vastata?" Must select `list_open_consultations`.
   - Spatial: "What is planned near Hakaniemi?" Must mention approximate locations.
   - Aggregation: "How many plans per year since 2020?" Must use `summarize_plans` rather than many searches.
   - Negative: "What did the committee decide about school budgets?" Out of scope, and must say so rather than guess.
   - Citation: every factual claim must carry a `source_url` that exists in the data.
5. **Metrics per model:**
   - Task success.
   - Tool-selection accuracy: first tool correct, and share of runs using an expected tool.
   - Tool calls per task, tokens per task, invalid-parameter rate.
   - Rate of unsupported claims.
   - Finnish against English gap.
   - Use these to decide on tool names, English or Finnish descriptions, and Snowball, Voikko or embeddings, rather than deciding by opinion.
6. **Data quality alongside.** Complete the unreviewed `data/quality_sample.csv` review. Until it is done, nobody can state classification accuracy. Eval results measure the server, not the truth of the data.

**Privacy-respecting usage measurement:**
- **Per request, keep:** timestamp rounded to the hour, tool name, status, duration bucket, result-count bucket, protocol version, and client name from `clientInfo` (self-declared, useful only as a rough breakdown).
- **Do not keep:** query text, place names, coordinates or full IP addresses. Disable or shorten platform access logs where possible, and note in the privacy policy what the hosting platform itself retains, since this may not be fully controllable on Cloud Run or a CDN.
- **Understanding what people ask for:** the useful signal is zero-result rate. Log a boolean, not the query. If query insight is truly needed, sample for a short period, publish the fact, and strip to matched gazetteer place and plan type rather than raw text.
- **Publishing:** aggregated daily counts could be committed like `update_log.md`, which matches the project's transparency habit.
- **Reach versus engagement:** hosted clients call from vendor IP ranges and have no sessions under the 2026-07-28 model, so "unique users" is **not measurable** without identifying people. Report calls and tool mix, and do not chase user counts.

### Gaps
- I did not run the conformance suite or the Inspector against the spike, only `curl`.
- I found no published target numbers for tool-selection accuracy, so the first eval run sets the baseline.
- I did not read the OpenTelemetry specification itself, and those attribute names may change.

## What is the recommended architecture for this project?

### Takeaway
A **single small Python container, stateless, with data baked in and an in-memory SQLite FTS5 index, running on Cloud Run in Finland**, with five read-only tools and no authentication. Expected cost is about EUR 0/month plus a domain, or a fixed EUR 6/month on Hetzner Helsinki. The build effort is small because the data and caveats already exist. My confidence in the shape is high, and medium in the Cloud Run over Hetzner choice, which depends on values rather than engineering.

### Cited Findings
- Stateless servers need no shared store or sticky routing — [MCP blog](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- One SDK app serves modern and legacy clients, and stateless mode suits tools that never call back — [Serving legacy clients](https://py.sdk.modelcontextprotocol.io/run/legacy-clients/)
- Anonymous access is accepted by Claude for public data — [Claude submission](https://claude.com/docs/connectors/building/submission)
- `GITHUB_TOKEN` commits do not trigger push workflows — [GitHub docs](https://docs.github.com/en/actions/concepts/security/github_token)
- Prices and regions are as in the hosting table above, seen 2026-11-02 — [Cloud Run](https://docs.cloud.google.com/run/pricing), [Hetzner](https://www.hetzner.com/cloud/cost-optimized/)

### Inferences

```
update-data.yml (unchanged: stdlib, commits data/)
        | workflow_run on success
        v
deploy-mcp.yml: validate data -> test -> build image (code + data/) -> deploy via OIDC
        v
Cloud Run europe-north1  (max-instances=1, public, TLS)
  mcp_server/server.py      mcp 2.x, stateless, hash-pinned   <- only non-stdlib code
  lautakuntamuistiot/query.py   stdlib: JSON load, FTS5 :memory:, gazetteer, haversine, provenance
        ^ POST https://<domain>/mcp   (GET returns 405)
Claude / ChatGPT / VS Code / Cursor / Antigravity CLI
```

**Options summary:**

| Decision | Recommended | Alternative | Why |
|---|---|---|---|
| Protocol | Dual era through SDK, stateless | Modern only | Legacy clients cannot fall forward, and hosted client era is unconfirmed |
| Framework | Official `mcp` 2.x | FastMCP, or stdlib-only server | Fewest moving parts that still track the spec |
| Isolation | `mcp_server/` directory with its own lock file | `pyproject` optional extra | Keeps "nothing to pip install" true for the scrapers |
| Data | JSON into in-memory FTS5 at startup | Plain Python scan for a first prototype | 15 ms build, stdlib only |
| Finnish | Gazetteer + prefix + hints | Snowball, then build-time Voikko | Add only if evals show the need |
| Vector | None | Later, if evals demand it | Thin evidence, high cost |
| Auth | None | API keys if abused | Public data, lowest friction |
| Update | Rebuild image via `workflow_run` | Hetzner pull with atomic swap | Avoids the `GITHUB_TOKEN` trap, and gives versioned data |
| Host | Cloud Run Finland, about $0 | Hetzner Helsinki EUR 5.99, Fly `arn` about $3 to $5 | See hosting section |

**Phases:**
1. **Spike to private trial (days):** query core with tests, five tools, Inspector, a custom connector in Claude, and the first 20 evals.
2. **Public beta:** domain, privacy policy, Finnish instructions for Claude and ChatGPT, provenance review, abuse limits, minimal metrics, the rest of the evals, and a README section. Publish to the official registry.
3. **Directories:** Anthropic Connectors Directory first, then consider the ChatGPT `search`/`fetch` path and OpenAI submission, after checking the "not a trial or demo" rule against the project's wording.
4. **Optional:** the zoning archive, an MCP App map view, and better Finnish analysis if evals call for it.

**Decisions needed from the project owner:**
- Who is the named operator, and is a domain being bought? Directory listings and the privacy policy need an accountable contact, and a domain gives a stable URL and DNS namespace.
- Is a US-owned platform acceptable? If not, choose Hetzner.
- Is the zoning archive in scope for v1?
- Is the `data/quality_sample.csv` review done before a public launch? I recommend yes, so the service can state measured accuracy instead of none.

### Gaps
- **Untested end to end:** the spike ran only on localhost with `curl`. Connecting real Claude and ChatGPT clients to a deployed endpoint is the first thing to verify, since their era and timeout behaviour are undocumented.
- Maintenance burden over time is not quantifiable from sources. The SDK v2 rename and the stateless protocol change both landed in 2026, so budget for periodic upgrades.
- Demand is out of scope for this note, and these figures say nothing about whether users will connect it.
