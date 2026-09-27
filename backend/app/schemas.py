from typing import Optional

from pydantic import BaseModel


class Project(BaseModel):
    id: str
    symbol: str
    name: str
    image: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    fully_diluted_valuation: Optional[float] = None
    total_volume: Optional[float] = None
    total_value_locked: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    preview_listing: bool = False
