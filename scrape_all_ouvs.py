import asyncio
import pandas as pd
from playwright.async_api import async_playwright, Page
from unesco_fetcher import create_stealth_browser, wait_for_cloudflare, UNESCO_LIST_URL
import logging
from bs4 import BeautifulSoup
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

async def fetch_ouv_from_main(page: Page, url: str, site_id: int) -> str:
    """Fetch the main page and extract the exact OUV section."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        # Wait a bit for cloudflare check just in case, though usually not needed if warmed up
        if "Attention Required" in await page.title():
            await wait_for_cloudflare(page)
            
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Find the OUV heading
        headings = soup.find_all(re.compile('^h[1-6]$'), string=re.compile('Outstanding Universal Value', re.I))
        if headings:
            h = headings[0]
            next_node = h.find_next_sibling()
            if next_node and next_node.name == 'div' and 'rich-text' in next_node.get('class', []):
                return next_node.get_text(separator="\n\n", strip=True)
            elif next_node:
                # Fallback if it's not a div.rich-text
                return next_node.get_text(separator="\n\n", strip=True)
        
        # Fallback to the old method if there's an #ouv div
        ouv_div = soup.find(id='ouv') or soup.find(class_='ouv-content')
        if ouv_div:
            return ouv_div.get_text(separator="\n\n", strip=True)
            
        return ""
    except Exception as e:
        err_msg = str(e)
        if "Target page, context or browser has been closed" in err_msg or "Browser closed" in err_msg or "Connection closed" in err_msg:
            raise e
        logger.warning(f"Failed to fetch OUV for {site_id} from {url}: {e}")
        return ""

async def main():
    csv_path = 'data/unesco_world_heritage_sites.csv'
    df = pd.read_csv(csv_path)
    
    total = len(df)
    logger.info(f"Starting full OUV scrape from main URLs for {total} sites.")
    
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        
        logger.info("Warming up browser session (Cloudflare pass)...")
        await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded", timeout=120000)
        await wait_for_cloudflare(page, context=context, timeout_ms=20000)
        
        idx = 0
        while idx < total:
            row = df.iloc[idx]
            site_id = int(row['unesco_id'])
            
            # Some URLs were NaN in the CSV, just construct it properly
            url = f"https://whc.unesco.org/en/list/{site_id}"
            
            # Skip if we already successfully fetched the FULL OUV (>8000 chars means we definitely did, 
            # or if we already ran it in the previous pass we don't want to re-run 1176 sites again)
            # Actually, to make it fast, let's just resume from index 1150 to be safe
            if idx < 1150:
                idx += 1
                continue
                
            logger.info(f"[{idx+1}/{total}] Fetching full OUV for site {site_id}: {url}")
            
            try:
                ouv_text = await fetch_ouv_from_main(page, url, site_id)
                if ouv_text:
                    df.at[idx, 'ouv_statement'] = ouv_text
                else:
                    if pd.isna(df.at[idx, 'ouv_statement']):
                        df.at[idx, 'ouv_statement'] = ""
            except Exception as e:
                err_msg = str(e)
                if "Target page, context or browser has been closed" in err_msg or "Browser closed" in err_msg or "Connection closed" in err_msg:
                    logger.warning(f"Browser crashed at site {site_id}. Recreating browser...")
                    try:
                        await browser.close()
                    except:
                        pass
                    browser, context, page = await create_stealth_browser(p)
                    logger.info("Re-warming up browser...")
                    try:
                        await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded")
                        await wait_for_cloudflare(page, context=context, timeout_ms=20000)
                    except Exception as warmup_e:
                        logger.error(f"Failed to warmup during retry: {warmup_e}")
                    continue # Retry the same site
                else:
                    logger.warning(f"Unhandled error for {site_id}: {e}")
            
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
    logger.info("Finished fetching all OUVs.")

if __name__ == "__main__":
    asyncio.run(main())
