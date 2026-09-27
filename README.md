# Crypto Screener

A small full-stack app that screens CoinGecko's coin universe against a fixed
set of criteria and lets you further filter/search/sort the result from the
frontend.

- **Backend:** Python, FastAPI
- **Frontend:** React (Vite)

## Project structure

```
backend/    FastAPI app — fetches, filters and serves project data
frontend/   React app — talks only to the backend, never to CoinGecko directly
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

**Frontend**

- Displays the screened project list (name, price, market cap, FDV, 24h
  volume, TVL) in a table.
- FDV max filter, name/symbol search (partial match, e.g. `eth` → Ethereum),
  and sort by market cap or 24h volume — all forwarded to the backend as
  query params, debounced by 300ms.
- Loading and error states; no external API calls from the browser.

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
- Basic backend tests (filter logic is pure and easy to unit test).
- Debounce the FDV number input specifically (currently all inputs share one
  300ms debounce), and add a small loading skeleton instead of a text swap.

## AI workflow

- **Tools used:** Claude Code (Sonnet 5), as an interactive CLI agent with
  direct file/terminal access.
- **How:** Pasted the task brief directly into Claude Code and had it design
  and build both the backend and frontend end-to-end — scaffolding the
  FastAPI app, writing the CoinGecko/DeFiLlama integration, and hand-writing
  the React app (Node wasn't available in this environment to scaffold via
  `npm create vite`, so the Vite/React files were written directly).
- **Where it helped most:** discovering in real time that CoinGecko's
  `/coins/list/new` endpoint (needed for `preview_listing`) is Pro-only, and
  that per-coin TVL isn't in CoinGecko at all — both found by actually
  calling the endpoints with `curl` during development rather than assuming
  the docs matched the free tier, then pivoting to DeFiLlama for TVL and
  documenting the `preview_listing` gap instead of silently guessing.
- **What I reviewed/corrected manually:** verified the backend against the
  real CoinGecko API (hit rate limits once during testing, which led to
  adding retry/backoff and a smaller page count), inspected actual filtered
  output to confirm the criteria were applied correctly, and reviewed all
  generated code before committing.
