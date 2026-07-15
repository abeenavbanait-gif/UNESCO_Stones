import asyncio
import logging
import json
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

# We will reuse the stealth setup from unesco_fetcher
from unesco_fetcher import create_stealth_browser, wait_for_cloudflare, UNESCO_LIST_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

async def fetch_ouv_only(page: Page, site_id: int) -> str:
    """Fetch only the OUV page for a site."""
    ouv_url = f"https://whc.unesco.org/en/list/{site_id}/ouv/"
    try:
        await page.goto(ouv_url, wait_until="domcontentloaded", timeout=15000)
        # Wait for either #ouv or the page body
        try:
            await page.wait_for_selector("#ouv, body", timeout=3000)
        except PlaywrightTimeoutError:
            pass

        ouv_text = await page.evaluate('''() => {
            const ouvDiv = document.querySelector("#ouv");
            if (ouvDiv) return ouvDiv.innerText;
            return "";
        }''')
        return ouv_text.strip() if ouv_text else ""
    except Exception as e:
        err_msg = str(e)
        if "Target page, context or browser has been closed" in err_msg or "Browser closed" in err_msg:
            raise e
        logger.warning(f"Failed to fetch OUV for {site_id}: {e}")
        return ""

async def main():
    csv_path = Path("data/unesco_world_heritage_sites.csv")
    df = pd.read_csv(csv_path)
    
    # Identify sites needing OUV fix
    # Missing OUV or truncated OUV (around 8000 chars)
    mask = df['ouv_statement'].isnull() | (df['ouv_statement'] == '') | (df['ouv_statement'].str.len() >= 7990)
    sites_to_fix = df[mask].copy()
    
    total = len(sites_to_fix)
    logger.info(f"Found {total} sites needing OUV fix.")
    
    if total == 0:
        return
        
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        
        logger.info("Warming up browser session (Cloudflare pass)...")
        await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded")
        await wait_for_cloudflare(page, context=context, timeout_ms=20000)
        
        idx = 0
        while idx < total:
            index = sites_to_fix.index[idx]
            row = sites_to_fix.iloc[idx]
            site_id = int(row['unesco_id'])
            logger.info(f"[{idx+1}/{total}] Fetching OUV for site {site_id}: {row['site_name'][:50]}")
            
            try:
                ouv_text = await fetch_ouv_only(page, site_id)
                if ouv_text:
                    df.at[index, 'ouv_statement'] = ouv_text
                else:
                    if pd.isna(df.at[index, 'ouv_statement']):
                        df.at[index, 'ouv_statement'] = ""
            except Exception as e:
                err_msg = str(e)
                if "Target page, context or browser has been closed" in err_msg or "Browser closed" in err_msg:
                    logger.warning(f"Browser crashed at site {site_id}. Recreating browser...")
                    try:
                        await browser.close()
                    except:
                        pass
                    browser, context, page = await create_stealth_browser(p)
                    logger.info("Re-warming up browser...")
                    await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded")
                    await wait_for_cloudflare(page, context=context, timeout_ms=20000)
                    continue # Retry the same site
                else:
                    logger.warning(f"Failed to fetch OUV for {site_id}: {e}")
                    if pd.isna(df.at[index, 'ouv_statement']):
                        df.at[index, 'ouv_statement'] = ""
            
            # Save progress every 50 sites
            if (idx + 1) % 50 == 0:
                logger.info("Checkpointing CSV...")
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
            await asyncio.sleep(0.5)
            idx += 1
            
        try:
            await browser.close()
        except:
            pass
        
    # Final save
    df.to_csv(csv_path, index=False, encoding='utf-8')
    logger.info(f"Finished fixing OUVs. Saved to {csv_path}")
    
    # Also update the JSON to match
    json_path = Path("data/unesco_master_list.json")
    records = df.to_dict(orient="records")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    logger.info(f"Updated JSON at {json_path}")

if __name__ == "__main__":
    asyncio.run(main())
