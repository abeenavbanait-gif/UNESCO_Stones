"""
unesco_fetcher.py — Step 1: Fetch all UNESCO World Heritage Sites.

Strategy:
  1. Attempt to load from UNESCO's XML syndication feed via Playwright
  2. For each site, fetch the individual page for OUV + description
  3. Full checkpoint/resume support for long-running scrapes
  4. Polite request intervals (configurable delay between requests)
  5. Uses playwright-stealth to bypass Cloudflare protection

Output: data/unesco_master_list.json
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add parent to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    CACHE_DIR,
    DATA_DIR,
    MASTER_LIST_CSV,
    MASTER_LIST_JSON,
    REQUEST_DELAY_SECONDS,
    UNESCO_BASE_URL,
    UNESCO_LIST_URL,
    UNESCO_SITE_URL_TEMPLATE,
    USER_AGENT,
)

logger = logging.getLogger(__name__)

# Cloudflare wait — must be long enough for challenge to auto-solve
CLOUDFLARE_WAIT_MS = 12000


# =====================================================================
# Helpers
# =====================================================================

def clean_text(text: str) -> str:
    """Collapse whitespace and strip."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_criteria(criteria_str: str) -> str:
    """
    Normalize criteria string to consistent format like '(i)(ii)(iv)'.
    Handles formats: 'C(i)(ii)', 'i, ii, iv', '(i)(ii)(iv)', etc.
    """
    if not criteria_str:
        return ""
    # Remove category prefixes
    criteria_str = re.sub(r"^[CNM]\s*", "", criteria_str.strip())
    # Find all roman numeral criteria
    found = re.findall(
        r"(i{1,3}|iv|vi{0,3}|ix|x)", criteria_str.lower()
    )
    if found:
        return "".join(f"({c})" for c in found)
    return criteria_str.strip()


def extract_year(year_str: str) -> int:
    """Extract the first 4-digit year from a string."""
    if not year_str:
        return 0
    match = re.search(r"(\d{4})", str(year_str))
    return int(match.group(1)) if match else 0


# =====================================================================
# Browser setup with Cloudflare bypass
# =====================================================================

async def create_stealth_browser(playwright):
    """
    Create a Playwright browser context with stealth settings
    to bypass Cloudflare bot detection.
    """
    from playwright_stealth import Stealth

    stealth = Stealth()

    browser = await playwright.chromium.launch(
        headless=False,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars'
        ]
    )
    
    state_path = CACHE_DIR / "state.json"
    context_kwargs = {
        "user_agent": USER_AGENT,
        "viewport": {"width": 1680, "height": 962},
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "java_script_enabled": True,
    }
    
    if state_path.exists():
        context_kwargs["storage_state"] = str(state_path)

    context = await browser.new_context(**context_kwargs)
    
    page = await context.new_page()
    await stealth.apply_stealth_async(page)
    return browser, context, page


async def wait_for_cloudflare(page, context=None, timeout_ms: int = CLOUDFLARE_WAIT_MS):
    """
    Wait for Cloudflare challenge to resolve.
    If a challenge is detected, prompts the user to solve it manually and waits longer.
    Saves the session state after passing.
    """
    try:
        # Check if we are currently on a challenge page
        text = await page.evaluate("() => document.body.innerText || ''")
        if "security verification" in text.lower() or "verifying you are human" in text.lower():
            logger.warning("=" * 80)
            logger.warning("CLOUDFLARE CHALLENGE DETECTED!")
            logger.warning("Please switch to the Chromium browser window and click the checkbox.")
            logger.warning("Waiting up to 120 seconds for manual verification...")
            logger.warning("=" * 80)
            timeout_ms = 120000  # Give user 2 minutes to solve it

        # Wait for either the content to appear or timeout
        await page.wait_for_function(
            """
            () => {
                const text = document.body.innerText || '';
                // Cloudflare challenge pages have this text
                if (text.includes('Performing security verification') ||
                    text.includes('Verifying you are human')) {
                    return false;
                }
                // Real UNESCO pages have content divs
                if (document.querySelector('#contentdes_en') ||
                    document.querySelector('.alternate') ||
                    text.length > 2000) {
                    return true;
                }
                return text.length > 1000;
            }
            """,
            timeout=timeout_ms,
        )
        
        # If we passed, save the state to persist the clearance cookie
        if context:
            state_path = CACHE_DIR / "state.json"
            await context.storage_state(path=str(state_path))
            
    except Exception as e:
        logger.warning("Cloudflare wait timeout or error: %s", e)
        # Fallback: just wait a bit more
        await page.wait_for_timeout(5000)


def parse_unesco_xml(xml_text: str) -> List[Dict[str, Any]]:
    """
    Parse UNESCO's XML syndication feed into site records.
    Uses BeautifulSoup for robust entity handling.
    """
    sites = []

    # The Playwright content() wraps XML in HTML. Try to extract raw XML.
    xml_match = re.search(r"(<\?xml.*?\?>.*)", xml_text, re.DOTALL)
    if xml_match:
        xml_text = xml_match.group(1)
    else:
        # Try to extract from HTML body
        body_match = re.search(r"<body[^>]*>(.*?)</body>", xml_text, re.DOTALL)
        if body_match:
            xml_text = body_match.group(1)

    # --- Strategy 1: Use BeautifulSoup for robust parsing ---
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(xml_text, "lxml-xml")
        rows = soup.find_all("row")
        if not rows:
            # Try HTML parser as fallback
            soup = BeautifulSoup(xml_text, "html.parser")
            rows = soup.find_all("row")

        logger.info("BeautifulSoup found %d <row> elements", len(rows))

        for row in rows:
            def get_bs_text(tag: str) -> str:
                elem = row.find(tag)
                return clean_text(elem.get_text()) if elem else ""

            site_id = get_bs_text("id_number")
            if not site_id:
                continue

            try:
                sid = int(site_id)
            except ValueError:
                continue

            # Parse coordinates from geolocations tag
            # Format: "lat1lon1cc1lat2lon2cc2..." — take first pair
            lat, lon = None, None
            geo_text = get_bs_text("geolocations")
            if geo_text:
                geo_match = re.match(
                    r"(-?\d+\.\d+)(-?\d+\.\d+)",
                    geo_text,
                )
                if geo_match:
                    try:
                        lat = float(geo_match.group(1))
                        lon = float(geo_match.group(2))
                    except ValueError:
                        pass

            # Clean HTML from short_description
            desc_raw = get_bs_text("short_description")
            # Strip residual HTML tags
            desc_clean = re.sub(r"<[^>]+>", "", desc_raw).strip()

            sites.append({
                "unesco_id": sid,
                "site_name": get_bs_text("site"),
                "country": get_bs_text("states"),
                "region": get_bs_text("regions"),
                "year_inscribed": extract_year(get_bs_text("date_inscribed")),
                "category": get_bs_text("category"),
                "criteria": parse_criteria(get_bs_text("criteria_txt")),
                "latitude": lat,
                "longitude": lon,
                "is_endangered": get_bs_text("danger") == "1",
                "is_transnational": get_bs_text("transnational") == "1",
                "iso_code": get_bs_text("iso_code"),
                "unesco_url": get_bs_text("http_url") or f"{UNESCO_BASE_URL}/en/list/{sid}",
                "ouv_statement": "",
                "brief_description": desc_clean,
                "date_fetched": date.today().isoformat(),
            })

        if sites:
            return sites
    except Exception as e:
        logger.warning("BeautifulSoup XML parsing failed: %s", e)

    # --- Strategy 2: Fallback to regex-based extraction ---
    logger.info("Attempting regex-based XML extraction...")
    row_pattern = re.compile(r"<row>(.*?)</row>", re.DOTALL)
    for row_match in row_pattern.finditer(xml_text):
        row_text = row_match.group(1)

        def get_tag(tag: str) -> str:
            m = re.search(
                rf"<{tag}>(.*?)</{tag}>", row_text, re.DOTALL
            )
            return clean_text(m.group(1)) if m else ""

        site_id = get_tag("id_number")
        if not site_id:
            continue

        try:
            sid = int(site_id)
        except ValueError:
            continue

        lat, lon = None, None
        geo_text = get_tag("geolocations")
        if geo_text:
            geo_match = re.match(r"(-?\d+\.\d+)(-?\d+\.\d+)", geo_text)
            if geo_match:
                try:
                    lat = float(geo_match.group(1))
                    lon = float(geo_match.group(2))
                except ValueError:
                    pass

        desc_raw = get_tag("short_description")
        desc_clean = re.sub(r"<[^>]+>", "", desc_raw).strip()

        sites.append({
            "unesco_id": sid,
            "site_name": get_tag("site"),
            "country": get_tag("states"),
            "region": get_tag("regions"),
            "year_inscribed": extract_year(get_tag("date_inscribed")),
            "category": get_tag("category"),
            "criteria": parse_criteria(get_tag("criteria_txt")),
            "latitude": lat,
            "longitude": lon,
            "is_endangered": get_tag("danger") == "1",
            "is_transnational": get_tag("transnational") == "1",
            "iso_code": get_tag("iso_code"),
            "unesco_url": get_tag("http_url") or f"{UNESCO_BASE_URL}/en/list/{sid}",
            "ouv_statement": "",
            "brief_description": desc_clean,
            "date_fetched": date.today().isoformat(),
        })

    return sites


# =====================================================================
# Playwright-based scraper
# =====================================================================


async def fetch_xml_feed_playwright() -> Tuple[str, List[Dict[str, Any]]]:
    """
    Fetch the UNESCO XML syndication feed using Playwright
    to bypass Cloudflare protection.

    Returns (raw_xml, parsed_sites).
    """
    from playwright.async_api import async_playwright

    xml_text = ""
    sites = []

    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)

        logger.info("Fetching UNESCO XML syndication feed...")
        try:
            await page.goto(
                f"{UNESCO_BASE_URL}/en/list/xml/",
                wait_until="domcontentloaded",
                timeout=60000,
            )
            await wait_for_cloudflare(page, context=context, timeout_ms=15000)
            xml_text = await page.content()

            if "<row>" in xml_text or "<id_number>" in xml_text:
                sites = parse_unesco_xml(xml_text)
                logger.info("XML feed parsed: %d sites", len(sites))
            else:
                logger.warning("XML feed did not contain expected tags")
        except Exception as e:
            logger.warning("XML feed fetch failed: %s", e)

        await browser.close()

    return xml_text, sites


async def fetch_all_sites_from_list_page() -> List[Dict[str, Any]]:
    """
    Scrape the UNESCO list page to get all site IDs.
    Uses the alphabetical list which shows all sites.
    """
    from playwright.async_api import async_playwright

    site_links: List[Dict[str, Any]] = []

    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)

        logger.info("Fetching UNESCO World Heritage list page...")
        await page.goto(
            f"{UNESCO_LIST_URL}",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        await wait_for_cloudflare(page, context=context)

        # Check if we got past Cloudflare
        body_text = await page.evaluate("() => document.body.innerText || ''")
        if "security verification" in body_text.lower():
            logger.warning("Still on Cloudflare challenge page after wait")
            await page.wait_for_timeout(10000)  # Extra wait

        # Extract all site links
        site_links = await page.evaluate("""
            () => {
                const links = [];
                document.querySelectorAll('a[href*="/en/list/"]').forEach(a => {
                    const href = a.getAttribute('href');
                    const match = href.match(/\\/en\\/list\\/(\\d+)/);
                    if (match) {
                        const id = parseInt(match[1]);
                        const name = a.textContent.trim();
                        if (name.length > 3 && id > 0) {
                            links.push({ id, name, url: 'https://whc.unesco.org' + href });
                        }
                    }
                });
                // Deduplicate by ID
                const seen = new Set();
                return links.filter(l => {
                    if (seen.has(l.id)) return false;
                    seen.add(l.id);
                    return true;
                });
            }
        """)

        logger.info("Found %d site links on list page", len(site_links))
        await browser.close()

    return site_links


async def fetch_site_detail(
    page: Any,
    site_id: int,
    delay: float = REQUEST_DELAY_SECONDS,
    context: Any = None,
) -> Dict[str, str]:
    """
    Fetch the detail page for a single UNESCO site.

    UNESCO structure (confirmed by live inspection):
      /en/list/{id}/      → description + sidebar metadata
      /en/list/{id}/ouv/  → full OUV statement (SEPARATE page — not on main!)
    """
    main_url = UNESCO_SITE_URL_TEMPLATE.format(site_id=site_id)
    ouv_url  = f"https://whc.unesco.org/en/list/{site_id}/ouv/"

    result: Dict[str, Any] = {
        "description": "", "ouv": "", "category": "", "criteria": "",
        "year": "", "country": "", "region": "", "full_text": "", "body_length": 0,
    }

    # ── Step 1: Main page ─────────────────────────────────────────────────
    try:
        await page.goto(main_url, wait_until="domcontentloaded", timeout=30000)
        await wait_for_cloudflare(page, context=context, timeout_ms=15000)
        await page.wait_for_timeout(int(delay * 500))

        blen = await page.evaluate("() => (document.body.innerText || '').length")
        if blen < 500:
            logger.warning("Site %d main page short (%d chars)", site_id, blen)
            await page.wait_for_timeout(5000)

        main_data = await page.evaluate("""
            () => {
                const d = {};
                const body = document.body.innerText || '';
                const descEl = document.querySelector('#contentdes_en') ||
                               document.querySelector('.alternate');
                d.description = descEl ? descEl.innerText.trim() : '';
                const cat = body.match(/Category[:\\s]+(Cultural|Natural|Mixed)/i);
                d.category = cat ? cat[1] : '';
                const crit = body.match(/Criteria[:\\s]+([\\(\\)ivxIVX,\\s]+)/i);
                d.criteria = crit ? crit[1].trim() : '';
                const yr = body.match(/(?:Date of Inscription|Inscribed)[:\\s]+(\\d{4})/i);
                d.year = yr ? yr[1] : '';
                const st = body.match(/State(?:s)?\\s*Part(?:y|ies)[:\\s]+([^\\n]+)/i);
                d.country = st ? st[1].trim() : '';
                const reg = body.match(/Region[:\\s]+([^\\n]+)/i);
                d.region = reg ? reg[1].trim() : '';
                d.full_text = body.substring(0, 20000);
                d.body_length = body.length;
                return d;
            }
        """)
        result.update(main_data)
    except Exception as e:
        logger.error("Site %d main page failed: %s", site_id, e)

    # ── Step 2: OUV sub-page ─────────────────────────────────────────────
    # The OUV statement lives exclusively at /en/list/{id}/ouv/ and is never
    # present on the main page. Must be fetched separately.
    try:
        await page.goto(ouv_url, wait_until="domcontentloaded", timeout=30000)
        await wait_for_cloudflare(page, context=context, timeout_ms=15000)
        await page.wait_for_timeout(int(delay * 500))

        ouv_data = await page.evaluate("""
            () => {
                const body = document.body.innerText || '';
                // Named OUV div (some pages)
                const el = document.querySelector('#ouv') ||
                           document.querySelector('[id*="ouv"]') ||
                           document.querySelector('.ouv-content');
                if (el) return { ouv: el.innerText.trim(), len: body.length };
                // Text-search fallback
                for (const kw of ['Brief synthesis', 'Outstanding Universal Value']) {
                    const i = body.indexOf(kw);
                    if (i !== -1) return { ouv: body.substring(i, i + 10000).trim(), len: body.length };
                }
                // Whole-page fallback (OUV pages have little else)
                return { ouv: body.length > 500 ? body.substring(0, 10000).trim() : '', len: body.length };
            }
        """)

        if ouv_data.get("ouv"):
            result["ouv"] = ouv_data["ouv"]
        logger.debug("Site %d OUV: %d body chars → %d OUV chars",
                     site_id, ouv_data.get("len", 0), len(result["ouv"]))
    except Exception as e:
        logger.warning("Site %d OUV page failed: %s", site_id, e)

    return result


# =====================================================================
# Checkpoint management
# =====================================================================


def load_checkpoint(checkpoint_path: Path) -> Dict[str, Any]:
    """Load existing checkpoint if available."""
    if checkpoint_path.exists():
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_ids": [], "sites": []}


def save_checkpoint(
    checkpoint_path: Path,
    sites: List[Dict[str, Any]],
    completed_ids: List[int],
) -> None:
    """Save progress checkpoint."""
    data = {
        "completed_ids": list(completed_ids),
        "sites": sites,
        "last_updated": date.today().isoformat(),
        "count": len(sites),
    }
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =====================================================================
# Main fetcher pipeline
# =====================================================================


async def fetch_all_sites(
    max_sites: int = 0,
    skip_detail: bool = False,
    force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    """
    Master fetch function: collect all UNESCO World Heritage Sites.

    1. Try XML syndication feed first
    2. Fall back to scraping list page for site IDs
    3. Fetch each site's detail page for OUV and description
    4. Saves checkpoints every 25 sites

    Args:
        max_sites: Limit number of sites (0 = all)
        skip_detail: If True, only get basic info from feed/list (no detail pages)
        force_refresh: If True, ignore existing checkpoint

    Returns:
        List of site dictionaries
    """
    from playwright.async_api import async_playwright

    checkpoint_path = CACHE_DIR / "fetch_checkpoint.json"

    # Check for existing data
    if not force_refresh and MASTER_LIST_JSON.exists():
        logger.info("Loading existing master list from %s", MASTER_LIST_JSON)
        with open(MASTER_LIST_JSON, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if existing and len(existing) > 100:
            logger.info("Loaded %d sites from cache", len(existing))
            return existing

    # Load checkpoint
    checkpoint = load_checkpoint(checkpoint_path) if not force_refresh else {
        "completed_ids": [], "sites": []
    }
    completed_ids = set(checkpoint.get("completed_ids", []))
    all_sites: List[Dict[str, Any]] = checkpoint.get("sites", [])

    logger.info(
        "Starting fetch. Checkpoint has %d sites, %d completed IDs.",
        len(all_sites), len(completed_ids),
    )

    # ----- Phase 1: Get the list of all site IDs -----

    # Try XML feed first
    xml_sites: List[Dict[str, Any]] = []
    try:
        _, xml_sites = await fetch_xml_feed_playwright()
        logger.info("XML feed yielded %d sites", len(xml_sites))
    except Exception as e:
        logger.warning("XML feed approach failed: %s", e)

    if xml_sites:
        # XML feed gave us basic data; use it as base
        # Build lookup of existing sites by ID
        existing_ids = {s["unesco_id"] for s in all_sites}
        for xs in xml_sites:
            if xs["unesco_id"] not in existing_ids:
                all_sites.append(xs)
                existing_ids.add(xs["unesco_id"])
        logger.info("After XML merge: %d total sites", len(all_sites))
    else:
        # Fallback: scrape list page for IDs
        logger.info("Falling back to list page scraping...")
        link_data = await fetch_all_sites_from_list_page()
        existing_ids = {s["unesco_id"] for s in all_sites}
        for ld in link_data:
            if ld["id"] not in existing_ids:
                all_sites.append({
                    "unesco_id": ld["id"],
                    "site_name": ld["name"],
                    "country": "",
                    "region": "",
                    "year_inscribed": 0,
                    "category": "",
                    "criteria": "",
                    "latitude": None,
                    "longitude": None,
                    "is_endangered": False,
                    "unesco_url": ld["url"],
                    "ouv_statement": "",
                    "brief_description": "",
                    "date_fetched": date.today().isoformat(),
                })
                existing_ids.add(ld["id"])

    if max_sites > 0:
        all_sites = all_sites[:max_sites]

    logger.info("Total sites to process: %d", len(all_sites))

    # ----- Phase 2: Fetch detail pages -----

    if not skip_detail:
        async with async_playwright() as p:
            browser, context, page = await create_stealth_browser(p)

            # Warm up: visit the main UNESCO page to establish session
            logger.info("Warming up browser session (Cloudflare pass)...")
            await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded")
            await wait_for_cloudflare(page, context=context, timeout_ms=20000)

            # Verify we got past Cloudflare
            warmup_text = await page.evaluate("() => document.body.innerText || ''")
            if "security verification" in warmup_text.lower():
                logger.warning("Cloudflare challenge still active after warmup. Waiting more...")
                await page.wait_for_timeout(15000)
                warmup_text = await page.evaluate("() => document.body.innerText || ''")

            if "World Heritage" in warmup_text or len(warmup_text) > 2000:
                logger.info("✓ Browser session established (body: %d chars)", len(warmup_text))
            else:
                logger.warning("⚠ May still be blocked. Body: %d chars", len(warmup_text))

            sites_needing_detail = [
                (i, s) for i, s in enumerate(all_sites)
                if not s.get("ouv_statement") and s["unesco_id"] not in completed_ids
            ]
            total = len(sites_needing_detail)
            logger.info("Fetching detail pages for %d sites...", total)

            success_count = 0
            fail_count = 0

            for batch_idx, (idx, site) in enumerate(sites_needing_detail):
                site_id = site["unesco_id"]
                logger.info(
                    "[%d/%d] Fetching site ID %d: %s",
                    batch_idx + 1, total, site_id,
                    site.get("site_name", "Unknown")[:60],
                )

                detail = await fetch_site_detail(
                    page, site_id, delay=REQUEST_DELAY_SECONDS, context=context
                )

                body_len = detail.get("body_length", 0)

                # Merge detail into site record
                if detail.get("description"):
                    all_sites[idx]["brief_description"] = (
                        detail["description"][:5000]
                    )
                    success_count += 1
                elif body_len > 1000:
                    # Got some content but couldn't parse description
                    # Store the full text snippet as description
                    full_text = detail.get("full_text", "")
                    if full_text:
                        all_sites[idx]["brief_description"] = full_text[:3000]
                    success_count += 1
                else:
                    fail_count += 1

                if detail.get("ouv"):
                    all_sites[idx]["ouv_statement"] = detail["ouv"][:8000]
                if detail.get("category") and not site.get("category"):
                    all_sites[idx]["category"] = detail["category"]
                if detail.get("criteria") and not site.get("criteria"):
                    all_sites[idx]["criteria"] = parse_criteria(
                        detail["criteria"]
                    )
                if detail.get("year") and not site.get("year_inscribed"):
                    all_sites[idx]["year_inscribed"] = extract_year(
                        detail["year"]
                    )
                if detail.get("country") and not site.get("country"):
                    all_sites[idx]["country"] = detail["country"]
                if detail.get("region") and not site.get("region"):
                    all_sites[idx]["region"] = detail["region"]

                # Store full text for later keyword analysis
                full_text = detail.get("full_text", "")
                if full_text and len(full_text) > 500:
                    cache_file = CACHE_DIR / f"site_{site_id}_text.txt"
                    cache_file.write_text(full_text, encoding="utf-8")

                completed_ids.add(site_id)

                # Checkpoint every 25 sites
                if (batch_idx + 1) % 25 == 0:
                    logger.info(
                        "Checkpoint at %d sites (success: %d, fail: %d)",
                        batch_idx + 1, success_count, fail_count,
                    )
                    save_checkpoint(
                        checkpoint_path, all_sites, list(completed_ids),
                    )

            logger.info(
                "Detail fetch complete. Success: %d, Failed: %d",
                success_count, fail_count,
            )
            await browser.close()

    # ----- Phase 3: Save final output -----

    logger.info("Saving %d sites to %s", len(all_sites), MASTER_LIST_JSON)
    with open(MASTER_LIST_JSON, "w", encoding="utf-8") as f:
        json.dump(all_sites, f, indent=2, ensure_ascii=False)

    # Also save as CSV
    try:
        import pandas as pd
        df = pd.DataFrame(all_sites)
        
        # User explicitly requested ALL fields (including OUV) in the CSV
        # and named the file 'unesco_world_heritage_sites.csv'
        csv_path = CACHE_DIR.parent / "data" / "unesco_world_heritage_sites.csv"
        
        df.to_csv(csv_path, index=False, encoding="utf-8")
        logger.info("CSV saved to %s", csv_path)
    except Exception as e:
        logger.warning("Failed to save CSV: %s", e)

    # Clean up checkpoint on completion
    save_checkpoint(checkpoint_path, all_sites, list(completed_ids))

    return all_sites


# =====================================================================
# CLI
# =====================================================================


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Fetch all UNESCO World Heritage Sites"
    )
    parser.add_argument(
        "--max", type=int, default=0,
        help="Max number of sites to fetch (0 = all)"
    )
    parser.add_argument(
        "--skip-detail", action="store_true",
        help="Skip fetching individual site detail pages"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force refresh, ignoring cached data"
    )

    args = parser.parse_args()
    asyncio.run(
        fetch_all_sites(
            max_sites=args.max,
            skip_detail=args.skip_detail,
            force_refresh=args.force,
        )
    )
