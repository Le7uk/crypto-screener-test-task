"""Thin HTTP clients for the external data sources this service depends on.

The public (free) CoinGecko API has two gaps relative to the task spec:
  - No boolean "preview_listing" field exists on /coins/markets, and the one
    endpoint that could supply it (/coins/list/new) is Pro-only.
  - No per-coin TVL figure is exposed.
TVL is filled in from DeFiLlama's public /protocols feed (matched back to a
CoinGecko id via its `gecko_id` field). preview_listing cannot be sourced for
free at all — see README for how that's handled.
"""

import asyncio
import time
from typing import Any

import httpx

from app.config import COINGECKO_API_KEY, COINGECKO_BASE_URL, CACHE_TTL_SECONDS, MARKET_PAGES, PAGE_SIZE

DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"

_cache: dict[str, tuple[float, Any]] = {}


async def _cached_get(cache_key: str, url: str, params: dict | None = None, headers: dict | None = None) -> Any:
    now = time.monotonic()
    cached = _cache.get(cache_key)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    # The free CoinGecko tier rate-limits aggressively; back off and retry
    # once or twice rather than failing the whole request on a 429.
    async with httpx.AsyncClient(timeout=20) as client:
        for attempt in range(3):
            response = await client.get(url, params=params, headers=headers)
            if response.status_code == 429 and attempt < 2:
                await asyncio.sleep(3 * (attempt + 1))
                continue
            response.raise_for_status()
            data = response.json()
            break

    _cache[cache_key] = (now, data)
    return data


def _coingecko_headers() -> dict:
    if COINGECKO_API_KEY:
        return {"x-cg-demo-api-key": COINGECKO_API_KEY}
    return {}


async def fetch_market_universe() -> list[dict]:
    """Market data (price, market cap, FDV, volume, supply) for the coin
    universe we screen, paginated across MARKET_PAGES pages of PAGE_SIZE
    coins each, ordered by market cap descending."""
    results: list[dict] = []
    for page in range(1, MARKET_PAGES + 1):
        if page > 1:
            await asyncio.sleep(1.5)  # stay under the free tier's rate limit
        data = await _cached_get(
            f"coingecko_markets_page_{page}",
            f"{COINGECKO_BASE_URL}/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": PAGE_SIZE,
                "page": page,
                "sparkline": "false",
            },
            headers=_coingecko_headers(),
        )
        if not data:
            break
        results.extend(data)
    return results


async def fetch_tvl_by_coingecko_id() -> dict[str, float]:
    """Map of CoinGecko id -> TVL (USD), sourced from DeFiLlama's protocol list."""
    data = await _cached_get("defillama_protocols", DEFILLAMA_PROTOCOLS_URL)
    tvl_by_id: dict[str, float] = {}
    for protocol in data:
        gecko_id = protocol.get("gecko_id")
        tvl = protocol.get("tvl")
        if gecko_id and isinstance(tvl, (int, float)):
            # A handful of protocols share a gecko_id across chains; keep the largest TVL seen.
            tvl_by_id[gecko_id] = max(tvl_by_id.get(gecko_id, 0), tvl)
    return tvl_by_id
