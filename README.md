# Crypto Screener

A small full-stack app that screens CoinGecko's coin universe against a fixed
set of criteria and lets you further filter/search/sort the result from the
frontend.

- **Backend:** Python, FastAPI
- **Frontend:** React (Vite)

## Project structure

```
backend/    FastAPI app — fetches, filters and serves project data
  tests/    pytest unit tests for the filter logic
frontend/   React app — talks only to the backend, never to CoinGecko directly
.github/    CI workflow that runs the backend tests on every push
```

## How to run

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://127.0.0.1:8000`. Try `GET /api/projects` directly,
or `GET /api/projects?search=eth&fdv_max=50000000&sort_by=market_cap&sort_order=asc`.

Optional environment variables (see `backend/.env.example`) can be exported
before starting uvicorn: `COINGECKO_API_KEY`, `CACHE_TTL_SECONDS`,
`MARKET_PAGES`, `FRONTEND_ORIGINS`.

To run the tests:

```bash
pip install -r requirements-dev.txt
pytest -v
```

### Frontend

Requires Node.js (18+) and npm.

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. It reads the backend URL from
`VITE_API_BASE_URL` (see `frontend/.env.example`); it defaults to
`http://127.0.0.1:8000` if unset, so no `.env` file is required for local dev
against the default backend port.

## What was completed

**Backend**

- `GET /api/projects` — fetches coin market data from CoinGecko (paginated,
  in-memory cached), enriches it with TVL from DeFiLlama, and applies the six
  required filters (market cap > 0, preview listing, max supply == total
  supply, FDV < $100M, 24h volume > $50k, TVL > $50k).
- Accepts optional query params — `fdv_max`, `search`, `sort_by`
  (`market_cap` | `total_volume`), `sort_order` (`asc` | `desc`) — so the
  frontend's extra filtering/sorting is served by the backend rather than
  calling CoinGecko directly.
- Responses are cached in memory for `CACHE_TTL_SECONDS` (default 60s) to
  avoid hammering the free-tier rate limits on every request.
- 14 pytest unit tests covering the filter logic (each core criterion,
  individually, plus the FDV/search/sort query filters), run in CI via
  GitHub Actions on every push touching `backend/`.

**Frontend**

- Displays the screened project list (name, price, market cap, FDV, 24h
  volume, TVL) in a table.
- FDV max filter and name/symbol search (partial match, e.g. `eth` →
  Ethereum), forwarded to the backend as query params, debounced by 300ms.
- Sortable **Market Cap** and **24h Volume** columns — click a header to
  sort by it, click again to flip direction (an active-sort arrow indicates
  the current column/direction), rather than a separate sort dropdown.
- A result count ("Showing N projects"), skeleton loading rows instead of a
  plain "Loading…" text, and a dedicated empty state; no external API calls
  from the browser.

## Assumptions & limitations

The task's filter criteria don't map 1:1 onto CoinGecko's **free** public
API, so two assumptions were necessary:

1. **`preview_listing`** — the free API has no such boolean field. The one
   endpoint that would supply "recently listed" coins (`/coins/list/new`) is
   Pro-only (confirmed while building this — it returns a 10005 "PRO API
   subscribers only" error on the free tier). Since this can't be verified
   without a paid key, the backend treats every coin as satisfying this
   criterion and calls it out explicitly (`Project.preview_listing` is always
   `true`, with a comment pointing here). **To do properly:** with a
   CoinGecko Pro key, swap in `/coins/list/new` to build a real allow-list of
   preview-listing coin ids.
2. **TVL (`total_value_locked`)** — CoinGecko doesn't expose per-coin TVL at
   all (free or paid). This is sourced from **DeFiLlama's free
   `/protocols` endpoint** instead, matched back to a CoinGecko id via its
   `gecko_id` field. Coins with no matching DeFiLlama protocol have no TVL
   figure and are excluded by the `TVL > $50k` filter (can't confirm what we
   don't have).

Other notes:

- The screened universe is the top `MARKET_PAGES × 250` coins by market cap
  (default 1,000). This comfortably covers the FDV < $100M range without
  paginating the entire ~17k-coin CoinGecko listing on every request, and
  keeps requests well under the free tier's rate limit.
- No database — data is fetched live from CoinGecko/DeFiLlama and cached in
  memory per-process. Fine for this scope; a real deployment would want a
  shared cache (Redis) instead.
- Styling is intentionally minimal, per the task's own guidance to prioritize
  working functionality over visual polish.

### If I had more time

- Real `preview_listing` support via a CoinGecko Pro key.
- Pagination/virtualized list on the frontend instead of one flat table.
- Debounce the FDV number input specifically (currently all inputs share one
  300ms debounce).
- A shared cache (Redis) instead of per-process in-memory caching, for a
  real multi-instance deployment.

## AI workflow

**Tools used:** Claude Code (Claude Sonnet 5), as my main pair-programming
tool for the whole task.

**How I used it:** I gave it the task brief directly and had it scaffold and
build the FastAPI backend and the React frontend, while I directed the
actual technical decisions — which CoinGecko endpoints to use, how to handle
the two fields the free CoinGecko API doesn't actually expose
(`preview_listing`, TVL), and what to prioritize given the time limit
(working, correctly-filtered data over pixel-perfect styling — per the
brief's own "delivery mindset" guidance).

**Where it helped most:** raw speed on boilerplate (FastAPI routing,
Pydantic schemas, the Vite/React setup — I didn't have Node.js installed on
this machine, so having it hand-write the frontend files directly saved me
from a slow detour into environment setup) and on the CoinGecko API surface,
which I'd have otherwise had to look up field-by-field in the docs myself.

**What I reviewed/corrected manually:** I insisted on hitting the real
CoinGecko/DeFiLlama endpoints with `curl` instead of trusting the API docs
blindly — that's how we caught that `/coins/list/new` (the only endpoint
that could supply `preview_listing`) is Pro-only, and that CoinGecko has no
per-coin TVL at all. Rather than let that slide, I had it document
`preview_listing` as an honest limitation and pivot to DeFiLlama's
`/protocols` feed for TVL, which is a real, verified integration rather than
a stub. I also ran into a genuine 429 rate-limit while testing, walked
through the fix (retry/backoff, smaller page count) with it, and read
through the filter logic, the generated tests, and the API responses myself
before writing this up and pushing.
