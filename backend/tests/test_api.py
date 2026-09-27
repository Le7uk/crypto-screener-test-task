from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SMALL_CAP = {
    "id": "small-cap-coin",
    "symbol": "scc",
    "name": "Small Cap Coin",
    "image": None,
    "current_price": 1.0,
    "market_cap": 10_000_000,
    "fully_diluted_valuation": 20_000_000,
    "total_volume": 100_000,
    "circulating_supply": 10_000_000,
    "total_supply": 10_000_000,
    "max_supply": 10_000_000,
}

FDV_TOO_HIGH = {
    **SMALL_CAP,
    "id": "too-big-fdv",
    "symbol": "big",
    "name": "Too Big FDV",
    "fully_diluted_valuation": 200_000_000,  # fails FDV < $100M
}

TVL_BY_ID = {"small-cap-coin": 60_000, "too-big-fdv": 60_000}


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.main.fetch_market_universe", new_callable=AsyncMock)
@patch("app.main.fetch_tvl_by_coingecko_id", new_callable=AsyncMock)
def test_projects_endpoint_applies_core_filters(mock_tvl, mock_markets):
    """End-to-end wiring: a coin failing FDV < $100M must not reach the response."""
    mock_tvl.return_value = TVL_BY_ID
    mock_markets.return_value = [SMALL_CAP, FDV_TOO_HIGH]

    response = client.get("/api/projects")

    assert response.status_code == 200
    assert [p["id"] for p in response.json()] == ["small-cap-coin"]


@patch("app.main.fetch_market_universe", new_callable=AsyncMock)
@patch("app.main.fetch_tvl_by_coingecko_id", new_callable=AsyncMock)
def test_projects_endpoint_forwards_search_query_param(mock_tvl, mock_markets):
    mock_tvl.return_value = TVL_BY_ID
    mock_markets.return_value = [SMALL_CAP]

    matching = client.get("/api/projects", params={"search": "small"})
    non_matching = client.get("/api/projects", params={"search": "nonexistent"})

    assert [p["id"] for p in matching.json()] == ["small-cap-coin"]
    assert non_matching.json() == []
