import os

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

# How long to cache CoinGecko/DeFiLlama responses in memory, in seconds.
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "60"))

# How much of the CoinGecko coin universe to screen. 4 pages x 250 = 1000
# coins by market cap, which comfortably covers the FDV < $100M range while
# staying under the free tier's aggressive rate limit.
MARKET_PAGES = int(os.getenv("MARKET_PAGES", "4"))
PAGE_SIZE = 250

FDV_MAX_USD = 100_000_000
VOLUME_24H_MIN_USD = 50_000
TVL_MIN_USD = 50_000

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
