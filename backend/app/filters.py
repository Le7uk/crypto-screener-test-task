from app.config import FDV_MAX_USD, TVL_MIN_USD, VOLUME_24H_MIN_USD
from app.schemas import Project


def build_projects(markets: list[dict], tvl_by_id: dict[str, float]) -> list[Project]:
    return [
        Project(
            id=m["id"],
            symbol=m["symbol"],
            name=m["name"],
            image=m.get("image"),
            current_price=m.get("current_price"),
            market_cap=m.get("market_cap"),
            fully_diluted_valuation=m.get("fully_diluted_valuation"),
            total_volume=m.get("total_volume"),
            total_value_locked=tvl_by_id.get(m["id"]),
            circulating_supply=m.get("circulating_supply"),
            total_supply=m.get("total_supply"),
            max_supply=m.get("max_supply"),
            # See README: the free CoinGecko API has no boolean preview_listing
            # field, so this criterion can't be verified and defaults to True.
            preview_listing=True,
        )
        for m in markets
    ]


def apply_core_filters(projects: list[Project]) -> list[Project]:
    """The fixed criteria required by the task spec (always applied)."""
    return [
        p
        for p in projects
        if p.market_cap is not None
        and p.market_cap > 0
        and p.preview_listing
        and p.max_supply is not None
        and p.total_supply is not None
        and p.max_supply == p.total_supply
        and p.fully_diluted_valuation is not None
        and p.fully_diluted_valuation < FDV_MAX_USD
        and p.total_volume is not None
        and p.total_volume > VOLUME_24H_MIN_USD
        and p.total_value_locked is not None
        and p.total_value_locked > TVL_MIN_USD
    ]


def apply_query_filters(
    projects: list[Project],
    fdv_max: float | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "desc",
) -> list[Project]:
    """Extra filtering/sorting the frontend asks for on top of the core list."""
    result = projects

    if fdv_max is not None:
        result = [p for p in result if p.fully_diluted_valuation is not None and p.fully_diluted_valuation <= fdv_max]

    if search:
        needle = search.strip().lower()
        result = [p for p in result if needle in p.name.lower() or needle in p.symbol.lower()]

    if sort_by in ("market_cap", "total_volume"):
        reverse = sort_order != "asc"
        result = sorted(result, key=lambda p: getattr(p, sort_by) or 0, reverse=reverse)

    return result
