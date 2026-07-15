"""
config.py — Shared configuration for the UNESCO scraper pipeline.
"""
from pathlib import Path

# ── Directories ────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent
DATA_DIR  = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"

# Create dirs if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# ── Output files ───────────────────────────────────────────────────────────
MASTER_LIST_JSON = DATA_DIR / "unesco_master_list.json"
MASTER_LIST_CSV  = DATA_DIR / "unesco_master_list.csv"

# ── UNESCO URLs ────────────────────────────────────────────────────────────
UNESCO_BASE_URL          = "https://whc.unesco.org"
UNESCO_LIST_URL          = "https://whc.unesco.org/en/list/?order=id&number=5000"
UNESCO_SITE_URL_TEMPLATE = "https://whc.unesco.org/en/list/{site_id}/"

# ── Request settings ───────────────────────────────────────────────────────
REQUEST_DELAY_SECONDS = 1.5   # polite delay between page loads

# Browser User-Agent (realistic Chrome on macOS)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
