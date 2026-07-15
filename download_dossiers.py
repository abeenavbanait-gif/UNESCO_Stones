import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output directory
DOSSIER_DIR = Path("data/dossiers")
DOSSIER_DIR.mkdir(parents=True, exist_ok=True)

async def download_dossier(unesco_id: str):
    """
    On-demand downloader for a specific UNESCO site's PDF dossier.
    Uses Playwright to bypass Cloudflare and fetch the Nomination File or Advisory Body Evaluation.
    """
    pdf_path = DOSSIER_DIR / f"{unesco_id}.pdf"
    if pdf_path.exists():
        logger.info(f"Dossier for {unesco_id} already exists.")
        return str(pdf_path)

    logger.info(f"Downloading dossier for site {unesco_id}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        
        try:
            from playwright_stealth import stealth_async
            page = await context.new_page()
            await stealth_async(page)
        except ImportError:
            page = await context.new_page()

        url = f"https://whc.unesco.org/en/list/{unesco_id}/documents/"
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            links = await page.locator("a").element_handles()
            
            target_element = None
            for link in links:
                text = await link.inner_text()
                href = await link.get_attribute("href")
                
                if text and href:
                    text_lower = text.lower()
                    if ("nomination file" in text_lower or "advisory body evaluation" in text_lower or "nomination" in text_lower):
                        target_element = link
                        break
                        
            if not target_element:
                logger.error(f"Could not find any Nomination or Advisory document link for {unesco_id}")
                await browser.close()
                return None
                
            href = await target_element.get_attribute("href")
            full_url = href if href.startswith("http") else f"https://whc.unesco.org{href}"
            logger.info(f"Target URL: {full_url}. Downloading binary blob...")
            
            response = await page.context.request.get(full_url)
            pdf_bytes = await response.body()
            
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            
            logger.info(f"Successfully downloaded to {pdf_path}")
            await browser.close()
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"Failed to download dossier for {unesco_id}: {e}")
            await browser.close()
            return None

if __name__ == "__main__":
    # Test for Taj Mahal (ID 252)
    asyncio.run(download_dossier("252"))
