from typing import Literal, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGINS
from app.external_clients import fetch_market_universe, fetch_tvl_by_coingecko_id
from app.filters import apply_core_filters, apply_query_filters, build_projects
from app.schemas import Project

app = FastAPI(title="Crypto Screener API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/projects", response_model=list[Project])
async def get_projects(
    fdv_max: Optional[float] = Query(None, description="Extra client-side FDV cap in USD"),
    search: Optional[str] = Query(None, description="Partial, case-insensitive match on name/symbol"),
    sort_by: Optional[Literal["market_cap", "total_volume"]] = Query(None),
    sort_order: Literal["asc", "desc"] = Query("desc"),
) -> list[Project]:
    markets = await fetch_market_universe()
    tvl_by_id = await fetch_tvl_by_coingecko_id()

    projects = build_projects(markets, tvl_by_id)
    projects = apply_core_filters(projects)
    projects = apply_query_filters(projects, fdv_max=fdv_max, search=search, sort_by=sort_by, sort_order=sort_order)

    return projects
