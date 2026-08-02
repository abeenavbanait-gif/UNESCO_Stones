import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging
from unesco_fetcher import create_stealth_browser, wait_for_cloudflare, UNESCO_LIST_URL
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def fetch_ouv_from_main(page, url: str, site_id: str) -> str:
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if "Attention Required" in await page.title():
            await wait_for_cloudflare(page)
            
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        # Method 1: Find the OUV heading
        headings = soup.find_all(re.compile('^h[1-6]$'), string=re.compile('Outstanding Universal Value', re.I))
        if headings:
            h = headings[0]
            next_node = h.find_next_sibling()
            if next_node and next_node.name == 'div' and 'rich-text' in next_node.get('class', []):
                return next_node.get_text(separator="\n\n", strip=True)
            elif next_node:
                return next_node.get_text(separator="\n\n", strip=True)
        
        # Method 2: #ouv div
        ouv_div = soup.find(id='ouv') or soup.find(class_='ouv-content')
        if ouv_div:
            return ouv_div.get_text(separator="\n\n", strip=True)
            
        return ""
    except Exception as e:
        logger.warning(f"Failed to fetch OUV for {site_id}: {e}")
        return ""

async def main():
    target_path = 'out_data_July_29/rescanned_built_geological_monuments.csv'
    df = pd.read_csv(target_path)
    
    # We will scrape ANY site whose OUV length is suspiciously short (< 3600 chars)
    # This guarantees we get the full text for anything that might still be a short description
    df['ouv_len'] = df['ouv_statement'].astype(str).str.len()
    missing_df = df[df['ouv_len'] < 3600]
    
    logger.info(f"Found {len(missing_df)} sites with potentially short/truncated OUVs.")
    if len(missing_df) == 0:
        return
        
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        logger.info("Warming up browser...")
        await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded")
        await wait_for_cloudflare(page, context=context, timeout_ms=20000)
        
        updates = 0
        for idx, row in missing_df.iterrows():
            site_id = str(row['unesco_id']).replace('.0', '')
            url = f"https://whc.unesco.org/en/list/{site_id}"
            logger.info(f"Scraping {site_id} - {row['site_name']}...")
            
            full_ouv = await fetch_ouv_from_main(page, url, site_id)
            if full_ouv and len(full_ouv) > len(str(row['ouv_statement'])):
                df.at[idx, 'ouv_statement'] = full_ouv
                updates += 1
                logger.info(f"  -> Successfully updated! New length: {len(full_ouv)}")
            else:
                logger.info(f"  -> No better OUV found (or site has no long OUV).")
                
            await asyncio.sleep(1) # delay
            
            # Save checkpoint
            if updates % 10 == 0:
                df.drop(columns=['ouv_len'], errors='ignore').to_csv(target_path, index=False)
                
        await browser.close()
        
    df = df.drop(columns=['ouv_len'], errors='ignore')
    df.to_csv(target_path, index=False)
    # Also update re-scan
    df.to_csv('re-scan/rescanned_built_geological_monuments.csv', index=False)
    logger.info(f"Done! Updated {updates} sites with full OUVs.")

if __name__ == "__main__":
    asyncio.run(main())
