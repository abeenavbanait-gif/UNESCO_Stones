import asyncio
import pandas as pd
from unesco_fetcher import create_stealth_browser, UNESCO_LIST_URL, wait_for_cloudflare
from bs4 import BeautifulSoup
import logging
from playwright.async_api import async_playwright
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def fetch_metadata(page, url, site_id):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        metadata = {
            'date_of_inscription': '',
            'criteria': '',
            'property_size': '',
            'buffer_zone_size': '',
            'dossier': ''
        }
        
        for strong_tag in soup.find_all('strong'):
            key_text = strong_tag.get_text(strip=True).replace(':', '').strip()
            
            # Map the scraped keys to our dataframe columns
            key_map = {
                'Date of Inscription': 'date_of_inscription',
                'Criteria': 'criteria',
                'Property': 'property_size',
                'Buffer zone': 'buffer_zone_size',
                'Dossier': 'dossier'
            }
            
            if key_text in key_map:
                col_name = key_map[key_text]
                parent_div = strong_tag.find_parent('div')
                if parent_div:
                    full_text = parent_div.get_text(separator=' ', strip=True)
                    value_text = full_text.replace(strong_tag.get_text(strip=True), '').strip()
                    value_text = re.sub(r'\s+', ' ', value_text)
                    metadata[col_name] = value_text
                    
        return metadata
    except Exception as e:
        err_msg = str(e)
        if "Target page, context or browser has been closed" in err_msg or "Browser closed" in err_msg or "Connection closed" in err_msg:
            raise e
        logger.warning(f"Failed to fetch metadata for {site_id} from {url}: {e}")
        return None

async def main():
    logger.info("Starting scrape for new metadata properties...")
    
    csv_file = 'data/unesco_world_heritage_sites.csv'
    df = pd.read_csv(csv_file)
    
    # Add columns if they don't exist
    new_cols = ['date_of_inscription', 'criteria', 'property_size', 'buffer_zone_size', 'dossier']
    for col in new_cols:
        if col not in df.columns:
            df[col] = ''
    
    # Ensure they are object type to avoid dtype issues
    for col in new_cols:
        df[col] = df[col].astype(object)
        
    total = len(df)
    
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        
        logger.info("Warming up browser session (Cloudflare pass)...")
        await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded", timeout=120000)
        await wait_for_cloudflare(page, context=context, timeout_ms=20000)
        
        idx = 0
        while idx < total:
            row = df.iloc[idx]
            site_id = int(row['unesco_id'])
            url = row['unesco_url']
            
            # Skip if we already scraped date_of_inscription and it's not empty/nan
            # This allows the script to safely resume if it crashes
            if pd.notna(row['date_of_inscription']) and str(row['date_of_inscription']).strip() != '':
                idx += 1
                continue
                
            logger.info(f"[{idx+1}/{total}] Fetching metadata for site {site_id}: {url}")
            
            try:
                metadata = await fetch_metadata(page, url, site_id)
                
                if metadata:
                    for col in new_cols:
                        df.at[idx, col] = metadata[col]
                    logger.info(f"Success for {site_id}: {metadata}")
                
                # Checkpoint every 20 sites to be safe
                if (idx + 1) % 20 == 0:
                    df.to_csv(csv_file, index=False)
                    logger.info("Checkpointing CSV...")
                
                idx += 1
                await page.wait_for_timeout(2000)
                
            except Exception as e:
                err_msg = str(e)
                if "Target page, context or browser has been closed" in err_msg or "Browser closed" in err_msg or "Connection closed" in err_msg:
                    logger.warning(f"Browser crashed. Recreating browser...")
                    try:
                        await browser.close()
                    except:
                        pass
                    browser, context, page = await create_stealth_browser(p)
                    logger.info("Re-warming Cloudflare...")
                    await page.goto(UNESCO_LIST_URL, wait_until="domcontentloaded", timeout=120000)
                    await wait_for_cloudflare(page, context=context, timeout_ms=20000)
                else:
                    logger.error(f"Unexpected error: {e}")
                    idx += 1
                    
        # Final save
        df.to_csv(csv_file, index=False)
        await browser.close()
        logger.info("Finished fetching all metadata.")

if __name__ == "__main__":
    asyncio.run(main())
