import asyncio
import pandas as pd
from unesco_fetcher import create_stealth_browser, UNESCO_LIST_URL, CACHE_DIR, wait_for_cloudflare
from bs4 import BeautifulSoup
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

async def fetch_ouv_from_main(page, url, site_id):
    """Fetch OUV directly from the main site page."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Look for the section with id="ouv" or headers containing "Outstanding Universal Value"
        ouv_content = []
        
        # Method 1: The standard OUV div block that UNESCO uses
        ouv_div = soup.find('div', id='ouv')
        if ouv_div:
            # Get all text from paragraphs within this div
            for p in ouv_div.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    ouv_content.append(text)
                    
        # Method 2: If no explicit div, look for headers containing OUV and grab subsequent paragraphs
        if not ouv_content:
            headers = soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
            for header in headers:
                if 'Outstanding Universal Value' in header.get_text() or 'Justification for Inscription' in header.get_text():
                    curr = header.find_next_sibling()
                    while curr and curr.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
                        text = curr.get_text(separator='\n\n', strip=True)
                        if text:
                            ouv_content.append(text)
                        curr = curr.find_next_sibling()
                    break
        
        # Method 3: Try grabbing content from specific description tabs
        if not ouv_content:
            desc_div = soup.find('div', class_='content')
            if desc_div:
                paragraphs = desc_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 50:  # Skip tiny fragments
                        ouv_content.append(text)
                        
        result = "\n\n".join(ouv_content)
        
        # Mark missing if empty
        if not result or len(result.strip()) < 10:
            return "MISSING_ON_WEBSITE"
            
        return result
        
    except Exception as e:
        err_msg = str(e)
        if "Target page, context or browser has been closed" in err_msg or "Browser closed" in err_msg or "Connection closed" in err_msg:
            raise e
        logger.warning(f"Failed to fetch OUV for {site_id} from {url}: {e}")
        return ""

async def main():
    logger.info("Starting scrape for missing OUVs...")
    
    df = pd.read_csv('data/missing_ouv_sites.csv')
    df_main = pd.read_csv('data/unesco_world_heritage_sites.csv')
    
    df['ouv_statement'] = df['ouv_statement'].astype(object)
    df_main['ouv_statement'] = df_main['ouv_statement'].astype(object)
    
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
            
            logger.info(f"[{idx+1}/{total}] Fetching OUV for site {site_id}: {url}")
            
            try:
                ouv_text = await fetch_ouv_from_main(page, url, site_id)
                
                if ouv_text == "MISSING_ON_WEBSITE":
                    logger.info(f"Site {site_id} confirmed to have NO Outstanding Universal Value listed on its webpage.")
                elif ouv_text:
                    logger.info(f"Successfully scraped OUV for {site_id} ({len(ouv_text)} chars)")
                    
                # Update both dataframes
                df.at[idx, 'ouv_statement'] = ouv_text
                df_main.loc[df_main['unesco_id'] == site_id, 'ouv_statement'] = ouv_text
                
                # Checkpoint
                df.to_csv('data/missing_ouv_sites.csv', index=False)
                df_main.to_csv('data/unesco_world_heritage_sites.csv', index=False)
                
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
                    
        await browser.close()
        logger.info("Finished fetching all missing OUVs.")

if __name__ == "__main__":
    asyncio.run(main())
