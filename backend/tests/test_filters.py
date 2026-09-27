from app.filters import apply_core_filters, apply_query_filters
from app.schemas import Project


def make_project(**overrides) -> Project:
    """A project that passes every core filter, unless overridden."""
    defaults = dict(
        id="test-coin",
        symbol="tst",
        name="Test Coin",
        market_cap=10_000_000,
        fully_diluted_valuation=20_000_000,
        total_volume=100_000,
        total_value_locked=100_000,
        total_supply=1_000_000,
        max_supply=1_000_000,
        preview_listing=True,
    )
    defaults.update(overrides)
    return Project(**defaults)


class TestApplyCoreFilters:
    def test_passing_project_is_kept(self):
        project = make_project()
        assert apply_core_filters([project]) == [project]

    def test_rejects_zero_market_cap(self):
        project = make_project(market_cap=0)
        assert apply_core_filters([project]) == []

    def test_rejects_non_preview_listing(self):
        project = make_project(preview_listing=False)
        assert apply_core_filters([project]) == []

    def test_rejects_max_supply_not_equal_total_supply(self):
        project = make_project(max_supply=2_000_000, total_supply=1_000_000)
        assert apply_core_filters([project]) == []

    def test_rejects_fdv_above_100m(self):
        project = make_project(fully_diluted_valuation=100_000_001)
        assert apply_core_filters([project]) == []

    def test_accepts_fdv_just_under_100m(self):
        project = make_project(fully_diluted_valuation=99_999_999)
        assert apply_core_filters([project]) == [project]

    def test_rejects_volume_at_or_below_50k(self):
        project = make_project(total_volume=50_000)
        assert apply_core_filters([project]) == []

    def test_rejects_tvl_at_or_below_50k(self):
        project = make_project(total_value_locked=50_000)
        assert apply_core_filters([project]) == []

    def test_rejects_missing_tvl(self):
        project = make_project(total_value_locked=None)
        assert apply_core_filters([project]) == []


class TestApplyQueryFilters:
    def test_fdv_max_excludes_projects_above_threshold(self):
        cheap = make_project(id="cheap", fully_diluted_valuation=1_000_000)
        pricey = make_project(id="pricey", fully_diluted_valuation=90_000_000)
        result = apply_query_filters([cheap, pricey], fdv_max=50_000_000)
        assert result == [cheap]

    def test_search_matches_name_case_insensitively(self):
        eth = make_project(id="ethereum", name="Ethereum", symbol="eth")
        btc = make_project(id="bitcoin", name="Bitcoin", symbol="btc")
        result = apply_query_filters([eth, btc], search="ETH")
        assert result == [eth]

    def test_search_matches_symbol_partially(self):
        project = make_project(id="ethereum", name="Ethereum", symbol="eth")
        result = apply_query_filters([project], search="th")
        assert result == [project]

    def test_sort_by_market_cap_descending_by_default(self):
        small = make_project(id="small", market_cap=1_000)
        big = make_project(id="big", market_cap=1_000_000)
        result = apply_query_filters([small, big], sort_by="market_cap")
        assert [p.id for p in result] == ["big", "small"]

    def test_sort_by_total_volume_ascending(self):
        low = make_project(id="low", total_volume=1_000)
        high = make_project(id="high", total_volume=1_000_000)
        result = apply_query_filters([high, low], sort_by="total_volume", sort_order="asc")
        assert [p.id for p in result] == ["low", "high"]
